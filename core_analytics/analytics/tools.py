import sqlalchemy
from warehouse.ingestion.config import load_ingestion_config
import pandas as pd
import time
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class ExecuteSQLInput(BaseModel):
    sql: str = Field(description="The SELECT SQL query to execute against the analytics warehouse.")

class ExecuteSQLToolExecutor:
    def __init__(self):
        config = load_ingestion_config()
        self.engine = sqlalchemy.create_engine(config.database_url)

    def execute(self, sql: str) -> pd.DataFrame:
        # Simple safety check
        if not sql.strip().upper().startswith("SELECT") and not sql.strip().upper().startswith("WITH"):
            raise ValueError(f"Only SELECT/WITH statements are allowed. LLM generated: {sql}")
        
        # Wrap SQL in sqlalchemy.text to ensure proper handling
        df = pd.read_sql(sqlalchemy.text(sql), self.engine.connect())
        
        print(f"\n[DEBUG] Executed SQL:\n{sql}\n")
        
        return df

_sql_executor = ExecuteSQLToolExecutor()

@tool("execute_sql", args_schema=ExecuteSQLInput)
def execute_sql_tool(sql: str) -> str:
    """Executes a SELECT SQL query against the database and returns the result as a string."""
    try:
        df = _sql_executor.execute(sql)
        return df.to_string()
    except Exception as e:
        return f"Error executing SQL: {str(e)}"

# Keep old class for backward compatibility during migration
class ExecuteSQLTool:
    def __init__(self):
        self.executor = _sql_executor
    def execute(self, sql: str) -> pd.DataFrame:
        return self.executor.execute(sql)
