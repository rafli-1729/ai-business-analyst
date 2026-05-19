"""
SqlValidator for validating and cleaning SQL queries.

Extracts SQL validation logic from sql_guard.
Provides read-only validation and extraction.
"""

from core_analytics.analytics.sql_guard import (
    validate_sql_is_read_only,
    SqlValidationError,
)


class SqlValidator:
    """
    Validates SQL for safety and compliance.

    Enforces:
    - Read-only SQL only
    - No dangerous keywords
    - Proper SQL structure
    """

    @staticmethod
    def validate_read_only(sql: str) -> str:
        """
        Validate SQL is read-only safe.

        Args:
            sql: SQL to validate

        Returns:
            Validated, cleaned SQL

        Raises:
            SqlValidationError: If SQL fails validation
        """
        return validate_sql_is_read_only(sql)

    @staticmethod
    def is_valid_read_only(sql: str) -> bool:
        """
        Check if SQL is valid read-only.

        Args:
            sql: SQL to check

        Returns:
            True if valid, False otherwise
        """
        try:
            validate_sql_is_read_only(sql)
            return True
        except SqlValidationError:
            return False
