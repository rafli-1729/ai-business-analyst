import pandas as pd
from sqlalchemy import create_engine, text


class DatabaseExecutor:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, connect_args={"sslmode": "require"})

    def run_select_query(self, sql: str) -> pd.DataFrame:
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchall()
            columns = result.keys()
        return pd.DataFrame(rows, columns=columns)
