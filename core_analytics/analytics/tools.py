import sqlalchemy
import logging
from warehouse.ingestion.config import load_ingestion_config
from infra.database.introspection import list_tables, describe_table
from core_analytics.analytics.sql_guard import validate_sql_is_read_only
import pandas as pd
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List, Optional

logger = logging.getLogger(__name__)

class ListTablesInput(BaseModel):
    schemas: List[str] = Field(default=["gold", "silver"], description="List of schemas to search for tables.")

class DescribeTableInput(BaseModel):
    schema_name: str = Field(description="The schema name (e.g., 'gold').")
    table_name: str = Field(description="The table name.")

class ExecuteSQLInput(BaseModel):
    sql: str = Field(description="The SELECT SQL query to execute. Must be read-only.")

class SampleRowsInput(BaseModel):
    schema_name: str = Field(description="The schema name.")
    table_name: str = Field(description="The table name.")
    n_rows: int = Field(default=5, description="Number of rows to sample.")

class DatabaseToolExecutor:
    def __init__(self):
        config = load_ingestion_config()
        self.engine = sqlalchemy.create_engine(config.database_url)
        self.last_df: Optional[pd.DataFrame] = None
        self.result_cache: dict[str, pd.DataFrame] = {}

    def clear_cache(self):
        self.result_cache = {}
        self.last_df = None

    def list_all_tables(self, schemas: List[str]) -> str:
        logger.info(f"Agent Action [list_tables]: Exploring schemas {schemas}")
        tables = list_tables(self.engine, schemas)
        if not tables:
            return "No tables found in specified schemas."
        output = []
        for t in tables:
            line = f"- {t['schema']}.{t['table']} ({t['type']})"
            # Only include description if it's not empty to save tokens
            if t.get("description"):
                line += f": {t['description']}"
            output.append(line)
        return "\n".join(output)

    def get_table_info(self, schema: str, table: str) -> str:
        logger.info(f"Agent Action [describe_table]: Introspecting {schema}.{table}")
        try:
            info = describe_table(self.engine, schema, table)
            output = [f"Table: {schema}.{table}"]
            
            if info.get("description"):
                output.append(f"Description: {info['description']}")
            
            output.append("\nColumns:")
            for col in info["columns"]:
                nullable = "NULL" if col["nullable"] == "YES" else "NOT NULL"
                line = f"  - {col['name']} ({col['type']}) {nullable}"
                if col.get("description"):
                    line += f" | Description: {col['description']}"
                output.append(line)
            
            if info["primary_keys"]:
                output.append(f"\nPrimary Keys: {', '.join(info['primary_keys'])}")
            
            if info["foreign_keys"]:
                output.append("\nForeign Keys:")
                for fk in info["foreign_keys"]:
                    output.append(f"  - {fk['column']} -> {fk['ref_schema']}.{fk['ref_table']}({fk['ref_column']})")
            
            return "\n".join(output)
        except Exception as e:
            return f"Error describing table: {str(e)}"

    def get_sample_rows(self, schema: str, table: str, n: int) -> str:
        logger.info(f"Agent Action [sample_rows]: Sampling {n} rows from {schema}.{table}")
        try:
            # Use quoted identifiers for schema and table to handle special characters or reserved words
            query = f'SELECT * FROM "{schema}"."{table}" LIMIT {n}'
            with self.engine.connect() as conn:
                df = pd.read_sql(sqlalchemy.text(query), conn)
            
            if df.empty:
                return f"Table {schema}.{table} is empty."
            
            return f"Sample rows from {schema}.{table}:\n\n" + df.to_markdown(index=False)
        except Exception as e:
            return f"Error sampling table: {str(e)}"

    def execute(self, sql: str) -> str:
        logger.info(f"Agent Action [execute_query]: Running SQL:\n{sql}")
        try:
            # Enforce read-only and extraction
            cleaned_sql = validate_sql_is_read_only(sql)
            
            # Add automatic limit if not present to protect against massive data
            if "LIMIT" not in cleaned_sql.upper():
                cleaned_sql = f"{cleaned_sql} LIMIT 100"
            
            with self.engine.connect() as conn:
                df = pd.read_sql(sqlalchemy.text(cleaned_sql), conn)
            
            self.last_df = df # Legacy support
            self.result_cache[sql.strip()] = df # Cache by SQL string for retrieval
            
            if df.empty:
                return "Query returned no results."
            
            return df.to_markdown(index=False)
        except Exception as e:
            return f"Error executing SQL: {str(e)}"

_executor = DatabaseToolExecutor()

@tool("list_warehouse_tables", args_schema=ListTablesInput)
def list_tables_tool(schemas: List[str] = ["gold", "silver"]) -> str:
    """Lists all available tables and views in the analytics warehouse schemas."""
    return _executor.list_all_tables(schemas)

@tool("describe_warehouse_table", args_schema=DescribeTableInput)
def describe_table_tool(schema_name: str, table_name: str) -> str:
    """Returns the schema, columns, and relationships (PK/FK) for a specific table. 
    It is recommended to use 'sample_warehouse_table' after this to see real data values."""
    return _executor.get_table_info(schema_name, table_name)

@tool("sample_warehouse_table", args_schema=SampleRowsInput)
def sample_table_tool(schema_name: str, table_name: str, n_rows: int = 5) -> str:
    """Returns a few sample rows from a table to understand data formats and values."""
    return _executor.get_sample_rows(schema_name, table_name, n_rows)

@tool("execute_analytical_query", args_schema=ExecuteSQLInput)
def execute_query_tool(sql: str) -> str:
    """Executes a read-only SELECT query and returns the results formatted as a markdown table."""
    return _executor.execute(sql)

# Legacy support for existing engine integrations
class ExecuteSQLTool:
    def __init__(self):
        self.executor = _executor
    def execute(self, sql: str) -> pd.DataFrame:
        cleaned_sql = validate_sql_is_read_only(sql)
        with self.executor.engine.connect() as conn:
            return pd.read_sql(sqlalchemy.text(cleaned_sql), conn)
