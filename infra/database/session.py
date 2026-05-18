import pandas as pd
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def get_connection(engine: Engine):
    return engine.connect()


class DatabaseExecutor:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, connect_args={"sslmode": "require"})

    def run_select_query(self, sql: str, limit: Optional[int] = None) -> pd.DataFrame:
        bounded_sql = sql
        params = {}

        if limit is not None:
            bounded_sql = f"SELECT * FROM ({sql}) AS nlq_result LIMIT :row_limit"
            params["row_limit"] = limit

        with self.engine.connect() as conn:
            result = conn.execute(text(bounded_sql), params)
            rows = result.fetchall()
            columns = result.keys()
        return pd.DataFrame(rows, columns=columns)
