"""
ResponseFormatterService for formatting query results.

Consolidates result formatting logic.
"""

from typing import Any, Optional
from pandas import DataFrame
from ai.services.result_formatter import (
    dataframe_to_rows,
    infer_chart_type,
)


class ResponseFormatterService:
    """
    Formats query results for API responses.

    Manages:
    - Row conversion
    - Chart type inference
    - Response building
    """

    @staticmethod
    def dataframe_to_rows(
        dataframe: DataFrame,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Convert DataFrame to row dictionaries.

        Args:
            dataframe: Query result DataFrame
            limit: Maximum rows to return

        Returns:
            List of row dictionaries
        """
        return dataframe_to_rows(dataframe, limit=limit)

    @staticmethod
    def infer_chart_type(dataframe: DataFrame) -> str:
        """
        Infer visualization chart type from data.

        Args:
            dataframe: Query result DataFrame

        Returns:
            Chart type string ('line', 'bar', 'table', etc.)
        """
        return infer_chart_type(dataframe)

    @staticmethod
    def is_truncated(
        dataframe: DataFrame,
        row_limit: Optional[int],
    ) -> bool:
        """
        Check if results are truncated.

        Args:
            dataframe: Query result DataFrame
            row_limit: Applied row limit

        Returns:
            True if results are truncated
        """
        if not row_limit:
            return False

        return len(dataframe.index) >= row_limit
