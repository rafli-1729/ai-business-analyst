"""
SqlExecutor for executing validated SQL queries.

Handles database execution and result retrieval.
Separates execution concerns from generation and validation.
"""

from typing import Optional
from pandas import DataFrame
from infra.database.session import DatabaseExecutor
from infra.observability.logger import timed


class SqlExecutor:
    """
    Executes SQL queries against the data warehouse.

    Manages:
    - Database connection execution
    - Result retrieval
    - Query result formatting
    """

    def __init__(self, database_url: str):
        """
        Initialize SQL executor.

        Args:
            database_url: Database connection URL
        """
        self.db = DatabaseExecutor(database_url)

    def execute_query(
        self,
        sql: str,
        limit: Optional[int] = None,
        request_id: str = "query_exec",
    ) -> DataFrame:
        """
        Execute SQL query and return results.

        Args:
            sql: Validated SQL to execute
            limit: Optional row limit
            request_id: Request tracking ID

        Returns:
            Query results as DataFrame
        """
        with timed(
            "db_exec_timing",
            request_id=request_id,
        ):
            dataframe = self.db.run_select_query(sql, limit=limit)

        return dataframe
