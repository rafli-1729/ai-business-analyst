from services.config import Settings
from services.db import DatabaseExecutor
from services.llm import LlmClient
from services.observability import log_event, new_request_id, timed
from services.schema_loader import load_schema_metadata, render_schema_for_prompt
from services.sql_cache import SqlCache
from services.sql_guard import validate_sql_is_read_only


class QueryService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.schema_metadata = load_schema_metadata()
        self.schema_version = self.schema_metadata.get("schema_version", "v1")
        self.schema_text = render_schema_for_prompt(self.schema_metadata)
        self.cache = SqlCache(ttl_seconds=settings.sql_cache_ttl_s)
        self.llm = LlmClient(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            model=settings.llm_model,
            timeout_s=settings.llm_timeout_s,
            max_retries=settings.llm_max_retries,
            temperature=settings.llm_temperature,
        )
        self.db = DatabaseExecutor(settings.database_url)

    def _build_prompt(self, question: str) -> str:
        return f"""
You are a PostgreSQL expert.
Convert the user question into SQL.
Return ONLY SQL query without explanations.
Prefer safe analytical queries.
Schema:
{self.schema_text}
Question:
{question}
"""

    def ask(self, question: str):
        request_id = new_request_id()
        if len(question) > self.settings.max_question_chars:
            raise ValueError(f"Question is too long. Max {self.settings.max_question_chars} chars")

        log_event("request_received", request_id=request_id, question=question[:200])

        sql = self.cache.get(question, self.schema_version)
        if sql:
            log_event("sql_cache_hit", request_id=request_id)
        else:
            with timed("llm_generate_timing", request_id=request_id):
                sql = self.llm.generate_sql(self._build_prompt(question), request_id=request_id)
            self.cache.set(question, self.schema_version, sql)

        validated_sql = validate_sql_is_read_only(sql)
        log_event("sql_validated", request_id=request_id)

        with timed("db_exec_timing", request_id=request_id):
            df = self.db.run_select_query(validated_sql)

        log_event("request_completed", request_id=request_id, row_count=len(df.index))
        return validated_sql, df
