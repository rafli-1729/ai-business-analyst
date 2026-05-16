"""
SummarizationService for generating query summaries.

Consolidates narrative summarization logic.
"""

import hashlib
from pathlib import Path
from typing import Any, Optional
from ai.services.llm import LlmClient
from ai.summarization.narrative import (
    summarize_query_result,
    summary_prompt_fingerprint,
)


class SummarizationService:
    """
    Generates narrative summaries of query results.

    Manages:
    - Summary generation via LLM
    - Summary versioning
    - Multi-step result summarization
    """

    def __init__(self, llm: LlmClient):
        """
        Initialize summarization service.

        Args:
            llm: LLM client for summary generation
        """
        self.llm = llm

    def summarize_query_result(
        self,
        question: str,
        sql: str,
        rows: list[dict[str, Any]],
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate summary of query results.

        Args:
            question: Original question
            sql: Generated SQL
            rows: Query result rows
            max_tokens: Optional token limit

        Returns:
            Summary text
        """
        return summarize_query_result(
            llm=self.llm,
            question=question,
            sql=sql,
            rows=rows,
            max_tokens=max_tokens,
        )

    @staticmethod
    def get_summary_fingerprint() -> str:
        """
        Get fingerprint for response versioning.

        Returns:
            Version fingerprint string
        """
        return summary_prompt_fingerprint()
