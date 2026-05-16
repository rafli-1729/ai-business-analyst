"""
AnalyticalOrchestrator for coordinating analytical workflows.

Central orchestration layer that coordinates:
- SQL generation
- Caching
- Validation and repair
- Execution
- Summarization
- Multi-step reasoning flows
"""

import time
from typing import Optional

from infra.config.settings import Settings
from infra.observability.logger import (
    log_event,
    new_request_id,
)

from ai.caches.sql_cache import SqlCache
from ai.caches.response_cache import ResponseCache
from ai.models.analytical_context import AnalyticalContext
from ai.models.execution_result import ExecutionResult
from ai.providers.schema_context_provider import SchemaContextProvider
from ai.validators.sql_validator import SqlValidator
from ai.executors.sql_executor import SqlExecutor
from ai.services.llm import LlmClient
from ai.services.prompt_composer import PromptComposer
from ai.services.sql_repair_service import SqlRepairService
from ai.services.response_formatter_service import ResponseFormatterService
from ai.services.summarization_service import SummarizationService


class AnalyticalOrchestrator:
    """
    Orchestrates analytical query workflows.

    Responsibilities:
    - Query planning and execution sequencing
    - Caching coordination
    - Agent selection and invocation
    - SQL generation and validation
    - Result formatting and summarization

    Does NOT:
    - Generate SQL directly
    - Access database infrastructure
    - Execute business logic
    """

    def __init__(self, settings: Settings):
        """
        Initialize orchestrator.

        Args:
            settings: Application settings
        """
        self.settings = settings

        # Core providers
        self.schema_provider = SchemaContextProvider()

        # Caching
        self.sql_cache = SqlCache(
            ttl_seconds=settings.sql_cache_ttl_s
        )

        # Services
        self.llm = LlmClient(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            model=settings.llm_model,
            timeout_s=settings.llm_timeout_s,
            max_retries=settings.llm_max_retries,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

        self.prompt_composer = PromptComposer(self.schema_provider)
        self.sql_repair = SqlRepairService(
            self.llm,
            self.prompt_composer,
        )
        self.sql_executor = SqlExecutor(settings.database_url)
        self.formatter = ResponseFormatterService()
        self.summarizer = SummarizationService(self.llm)

        # Validators
        self.sql_validator = SqlValidator()

    @property
    def schema_version(self) -> str:
        """Get current schema version."""
        return self.schema_provider.get_version()

    def execute_query(
        self,
        question: str,
        row_limit: Optional[int] = None,
        context: Optional[AnalyticalContext] = None,
        refresh: bool = False,
    ) -> ExecutionResult:
        """
        Execute a simple analytical query.

        Flow:
        1. Check response cache
        2. Check SQL cache
        3. Generate SQL
        4. Validate/repair SQL
        5. Execute query
        6. Format results
        7. Summarize

        Args:
            question: User question
            row_limit: Optional row limit
            context: Optional analytical context
            refresh: Bypass caching

        Returns:
            ExecutionResult with all details
        """
        execution_started = time.perf_counter()
        request_id = new_request_id()
        timings = {
            "sql_cache_lookup_ms": 0,
            "sql_prompt_build_ms": 0,
            "sql_generation_ms": 0,
            "sql_validation_ms": 0,
            "sql_cache_set_ms": 0,
            "db_execution_ms": 0,
            "formatting_ms": 0,
            "summarization_ms": 0,
        }

        # Validate question length
        if len(question) > self.settings.max_question_chars:
            raise ValueError(
                f"Question is too long. "
                f"Max {self.settings.max_question_chars} chars"
            )

        log_event(
            "query_execution_started",
            request_id=request_id,
            question=question[:200],
        )

        # PHASE 1: SQL CACHE LOOKUP
        cache_lookup_started = time.perf_counter()

        sql = self.sql_cache.get(question, self.schema_version)
        sql_cache_hit = bool(sql)

        timings["sql_cache_lookup_ms"] = int(
            (time.perf_counter() - cache_lookup_started) * 1000
        )

        if sql_cache_hit:
            log_event(
                "sql_cache_hit",
                request_id=request_id,
            )
        else:
            # PHASE 2: SQL GENERATION
            prompt_build_started = time.perf_counter()

            context_dict = context.to_dict() if context else {}
            agent_instructions = ""

            prompt = self.prompt_composer.build_sql_generation_prompt(
                question=question,
                context=context_dict,
                agent_instructions=agent_instructions,
            )

            timings["sql_prompt_build_ms"] = int(
                (time.perf_counter() - prompt_build_started) * 1000
            )

            # Generate SQL
            generation_started = time.perf_counter()

            sql = self.llm.generate_sql(
                prompt,
                request_id=request_id,
            )

            timings["sql_generation_ms"] = int(
                (time.perf_counter() - generation_started) * 1000
            )

            # PHASE 3: VALIDATION & REPAIR
            sql = self.sql_repair.repair_sql(
                question=question,
                generated_sql=sql,
                request_id=request_id,
                timings=timings,
            )

            # PHASE 4: CACHE SET
            cache_set_started = time.perf_counter()

            self.sql_cache.set(question, self.schema_version, sql)

            timings["sql_cache_set_ms"] = int(
                (time.perf_counter() - cache_set_started) * 1000
            )

            log_event(
                "sql_generated_and_validated",
                request_id=request_id,
            )

        # PHASE 5: EXECUTION
        execution_started_at = time.perf_counter()

        dataframe = self.sql_executor.execute_query(
            sql,
            limit=row_limit,
            request_id=request_id,
        )

        timings["db_execution_ms"] = int(
            (time.perf_counter() - execution_started_at) * 1000
        )

        # PHASE 6: FORMAT RESULTS
        format_started = time.perf_counter()

        rows = self.formatter.dataframe_to_rows(
            dataframe,
            limit=row_limit or 100,
        )

        is_truncated = self.formatter.is_truncated(dataframe, row_limit)
        chart_type = self.formatter.infer_chart_type(dataframe)

        timings["formatting_ms"] = int(
            (time.perf_counter() - format_started) * 1000
        )

        # PHASE 7: SUMMARIZATION
        summary_started = time.perf_counter()

        summary = self.summarizer.summarize_query_result(
            question=question,
            sql=sql,
            rows=rows,
            max_tokens=self.settings.summary_max_tokens,
        )

        timings["summarization_ms"] = int(
            (time.perf_counter() - summary_started) * 1000
        )

        # Build result
        total_ms = int(
            (time.perf_counter() - execution_started) * 1000
        )

        log_event(
            "query_execution_completed",
            request_id=request_id,
            row_count=len(dataframe.index),
            timings=timings,
        )

        result = ExecutionResult(
            request_id=request_id,
            question=question,
            sql=sql,
            dataframe=dataframe,
            summary=summary,
            timings={
                **timings,
                "orchestrator_total_ms": total_ms,
            },
            cache_hit=False,
            sql_cache_hit=sql_cache_hit,
            is_truncated=is_truncated,
            metadata={
                "chart_type": chart_type,
                "schema_version": self.schema_version,
                "model": self.settings.llm_model,
            },
        )

        return result
