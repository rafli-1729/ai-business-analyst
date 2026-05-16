"""
ExecutionResult model for capturing query execution outcomes.

Provides typed structure for storing SQL generation,
validation, and execution results with timing information.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from pandas import DataFrame


@dataclass
class ExecutionResult:
    """
    Execution result from SQL generation and query execution.

    Attributes:
        request_id: Unique request identifier
        question: Original question
        sql: Generated and validated SQL
        dataframe: Query result as DataFrame
        summary: Narrative summary of results
        timings: Timing metrics for each phase
        cache_hit: Whether result came from cache
        sql_cache_hit: Whether SQL came from SQL cache
        is_truncated: Whether results were truncated
        metadata: Additional execution metadata
    """

    request_id: str
    question: str
    sql: str
    dataframe: DataFrame

    summary: str = ""
    timings: dict[str, int] = field(default_factory=dict)
    cache_hit: bool = False
    sql_cache_hit: bool = False
    is_truncated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "request_id": self.request_id,
            "question": self.question,
            "sql": self.sql,
            "dataframe": self.dataframe,
            "summary": self.summary,
            "timings": self.timings,
            "cache_hit": self.cache_hit,
            "sql_cache_hit": self.sql_cache_hit,
            "is_truncated": self.is_truncated,
            "metadata": self.metadata,
        }
