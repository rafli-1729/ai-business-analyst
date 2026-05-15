import time

from click import prompt

from infra.config.settings import Settings
from infra.database.session import DatabaseExecutor

from infra.observability.logger import (
    log_event,
    new_request_id,
    timed,
)

from ai.services.llm import LlmClient
from ai.services.schema_loader import (
    load_schema_metadata,
    render_schema_for_prompt,
)
from ai.services.sql_cache import SqlCache
from ai.services.sql_guard import (
    SqlValidationError,
    validate_sql_is_read_only,
)


class QueryService:

    def __init__(self, settings: Settings):

        self.settings = settings

        self.schema_metadata = (
            load_schema_metadata()
        )

        self.schema_version = (
            self.schema_metadata.get(
                "schema_version",
                "v1",
            )
        )

        self.cache = SqlCache(
            ttl_seconds=settings.sql_cache_ttl_s
        )

        self.llm = LlmClient(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            model=settings.llm_model,
            timeout_s=settings.llm_timeout_s,
            max_retries=settings.llm_max_retries,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

        self.db = DatabaseExecutor(
            settings.database_url
        )

    def _build_prompt(
        self,
        question: str,
        context: dict | None = None,
    ) -> str:

        context_text = ""

        if context:

            context_text = f"""
            Analytical Context:
            {context}
            """

        return f"""
            You are a PostgreSQL analytics expert.

            Convert the user question into PostgreSQL SQL.

            Return ONLY PostgreSQL query.

            Rules:
            - Use PostgreSQL syntax.
            - Use read-only SQL only.
            - Prefer gold tables for business analytics.
            - Use silver tables for audits and validations.
            - Avoid bronze/raw unless explicitly requested.
            - Prefer simple and explainable SQL.
            - Do not return markdown.
            - Do not explain the query.
            - if you don't find any aggregations tables for the context,
              use the most relevant tables from the schema and aggregates it.

            {context_text}

            Schema:
            {render_schema_for_prompt(
                self.schema_metadata,
                question,
            )}

            Question:
            {question}
        """

    def ask(
        self,
        question: str,
        row_limit: int | None = None,
        context: dict | None = None,
    ):

        result = self.ask_with_metadata(
            question=question,
            row_limit=row_limit,
            context=context,
        )

        return (
            result["sql"],
            result["dataframe"],
        )

    def ask_with_metadata(
        self,
        question: str,
        row_limit: int | None = None,
        context: dict | None = None,
    ):

        service_started_at = (
            time.perf_counter()
        )

        request_id = new_request_id()

        timings = {
            "sql_cache_lookup_ms": 0,
            "sql_prompt_build_ms": 0,
            "sql_generation_ms": 0,
            "sql_validation_ms": 0,
            "sql_cache_set_ms": 0,
            "db_execution_ms": 0,
        }

        if (
            len(question)
            > self.settings.max_question_chars
        ):
            raise ValueError(
                f"Question is too long. "
                f"Max {self.settings.max_question_chars} chars"
            )

        log_event(
            "request_received",
            request_id=request_id,
            question=question[:200],
        )

        # CACHE LOOKUP

        started_at = time.perf_counter()

        sql = self.cache.get(
            question,
            self.schema_version,
        )

        timings["sql_cache_lookup_ms"] = int(
            (
                time.perf_counter()
                - started_at
            ) * 1000
        )

        sql_cache_hit = bool(sql)

        if sql:

            log_event(
                "sql_cache_hit",
                request_id=request_id,
            )

        else:

            # BUILD PROMPT

            started_at = time.perf_counter()

            prompt = self._build_prompt(
                question=question,
                context=context,
            )

            timings["sql_prompt_build_ms"] = int(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000
            )

            # GENERATE SQL

            started_at = time.perf_counter()

            with timed(
                "llm_generate_timing",
                request_id=request_id,
            ):

                sql = self.llm.generate_sql(
                    prompt,
                    request_id=request_id,
                )

            timings["sql_generation_ms"] = int(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000
            )

        validated_sql = (
            self._validate_or_repair_sql(
                question=question,
                sql=sql,
                request_id=request_id,
                timings=timings,
            )
        )

        # CACHE SET

        if not sql_cache_hit:

            started_at = time.perf_counter()

            self.cache.set(
                question,
                self.schema_version,
                validated_sql,
            )

            timings["sql_cache_set_ms"] = int(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000
            )

        log_event(
            "sql_validated",
            request_id=request_id,
        )

        # EXECUTE QUERY

        started_at = time.perf_counter()

        with timed(
            "db_exec_timing",
            request_id=request_id,
        ):

            dataframe = (
                self.db.run_select_query(
                    validated_sql,
                    limit=row_limit,
                )
            )

        timings["db_execution_ms"] = int(
            (
                time.perf_counter()
                - started_at
            ) * 1000
        )

        timings["query_service_total_ms"] = int(
            (
                time.perf_counter()
                - service_started_at
            ) * 1000
        )

        log_event(
            "request_completed",
            request_id=request_id,
            row_count=len(dataframe.index),
            timings=timings,
        )

        return {
            "request_id": request_id,
            "sql": validated_sql,
            "dataframe": dataframe,
            "timings": timings,
            "sql_cache_hit": sql_cache_hit,
            "is_truncated": bool(
                row_limit
                and len(dataframe.index)
                >= row_limit
            ),
        }

    def _validate_or_repair_sql(
        self,
        question: str,
        sql: str,
        request_id: str,
        timings: dict[str, int],
    ) -> str:

        validation_started_at = (
            time.perf_counter()
        )

        try:

            validated_sql = (
                validate_sql_is_read_only(sql)
            )

            timings["sql_validation_ms"] = int(
                (
                    time.perf_counter()
                    - validation_started_at
                ) * 1000
            )

            return validated_sql

        except SqlValidationError as exc:

            timings["sql_validation_ms"] = int(
                (
                    time.perf_counter()
                    - validation_started_at
                ) * 1000
            )

            log_event(
                "sql_validation_failed",
                request_id=request_id,
                error=str(exc),
                generated_sql_preview=sql[:500],
            )

            repair_prompt = f"""
                The previous SQL response was rejected by the validator.

                Return exactly one PostgreSQL read-only query.

                Rules:
                - Use only SELECT or WITH.
                - No markdown.
                - No explanations.
                - No comments.
                - No multiple statements.

                Validation error:
                {exc}

                Previous response:
                {sql}

                Original question:
                {question}

                Schema:
                {render_schema_for_prompt(
                    self.schema_metadata,
                    question,
                )}
            """

            repair_started_at = (
                time.perf_counter()
            )

            repaired_sql = (
                self.llm.generate_sql(
                    repair_prompt,
                    request_id=(
                        f"{request_id}:sql_repair"
                    ),
                )
            )

            timings[
                "sql_repair_generation_ms"
            ] = int(
                (
                    time.perf_counter()
                    - repair_started_at
                ) * 1000
            )

            repair_validation_started_at = (
                time.perf_counter()
            )

            validated_sql = (
                validate_sql_is_read_only(
                    repaired_sql
                )
            )

            timings[
                "sql_repair_validation_ms"
            ] = int(
                (
                    time.perf_counter()
                    - repair_validation_started_at
                ) * 1000
            )

            log_event(
                "sql_repaired",
                request_id=request_id,
            )

            return validated_sql