"""
SqlRepairService for repairing invalid SQL.

Handles SQL validation failures and repair attempts.
Extracts SQL repair logic from QueryService.
"""

import time
from ai.services.llm import LlmClient
from ai.validators.sql_validator import SqlValidator
from ai.services.prompt_composer import PromptComposer
from ai.services.sql_guard import SqlValidationError
from infra.observability.logger import log_event


class SqlRepairService:
    """
    Repairs SQL queries that fail validation.

    Manages:
    - SQL validation
    - Repair prompt generation
    - LLM-based repair
    - Repair validation
    """

    def __init__(
        self,
        llm: LlmClient,
        prompt_composer: PromptComposer,
    ):
        """
        Initialize SQL repair service.

        Args:
            llm: LLM client for repair generation
            prompt_composer: Prompt composer for repair prompts
        """
        self.llm = llm
        self.prompt_composer = prompt_composer
        self.validator = SqlValidator()

    def repair_sql(
        self,
        question: str,
        generated_sql: str,
        request_id: str = "repair",
        timings: dict | None = None,
    ) -> str:
        """
        Repair SQL that failed validation.

        Args:
            question: Original question
            generated_sql: Failed SQL
            request_id: Request tracking ID
            timings: Optional timing dict to populate

        Returns:
            Repaired and validated SQL

        Raises:
            SqlValidationError: If repair fails
        """
        if timings is None:
            timings = {}

        # Try initial validation
        validation_started = time.perf_counter()

        try:
            validated_sql = self.validator.validate_read_only(generated_sql)
            timings["sql_validation_ms"] = int(
                (time.perf_counter() - validation_started) * 1000
            )
            return validated_sql
        except SqlValidationError as exc:
            timings["sql_validation_ms"] = int(
                (time.perf_counter() - validation_started) * 1000
            )

            log_event(
                "sql_validation_failed",
                request_id=request_id,
                error=str(exc),
                generated_sql_preview=generated_sql[:500],
            )

            # Generate repair prompt
            repair_prompt = self.prompt_composer.build_sql_repair_prompt(
                question=question,
                original_sql=generated_sql,
                validation_error=str(exc),
            )

            # Generate repaired SQL
            repair_started = time.perf_counter()

            repaired_sql = self.llm.generate_sql(
                repair_prompt,
                request_id=f"{request_id}:sql_repair",
            )

            timings["sql_repair_generation_ms"] = int(
                (time.perf_counter() - repair_started) * 1000
            )

            # Validate repaired SQL
            repair_validation_started = time.perf_counter()

            validated_sql = self.validator.validate_read_only(repaired_sql)

            timings["sql_repair_validation_ms"] = int(
                (time.perf_counter() - repair_validation_started) * 1000
            )

            log_event(
                "sql_repaired",
                request_id=request_id,
            )

            return validated_sql
