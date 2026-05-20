import pytest
from unittest.mock import patch, MagicMock
from core_analytics.analytics.tools import _executor, execute_query_tool, list_tables_tool, describe_table_tool
import pandas as pd
from core_analytics.analytics.sql_guard import SqlValidationError

@patch("core_analytics.analytics.tools.sqlalchemy.create_engine")
def test_list_all_tables(mock_create_engine):
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    with patch("core_analytics.analytics.tools.list_tables") as mock_list:
        mock_list.return_value = [{"schema": "gold", "table": "sales", "type": "TABLE"}]
        result = _executor.list_all_tables(["gold"])
        
        assert "- gold.sales (TABLE)" in result

@patch("core_analytics.analytics.tools.sqlalchemy.create_engine")
def test_get_table_info_includes_descriptions(mock_create_engine):
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    with patch("core_analytics.analytics.tools.describe_table") as mock_desc:
        mock_desc.return_value = {
            "description": "Sales fact table",
            "columns": [{"name": "id", "type": "int", "nullable": "NO", "description": "Unique ID"}],
            "primary_keys": ["id"],
            "foreign_keys": []
        }
        result = _executor.get_table_info("gold", "sales")
        
        assert "Description: Sales fact table" in result
        assert "Description: Unique ID" in result

def test_execute_query_tool_adds_limit():
    with patch("core_analytics.analytics.tools._executor.engine.connect") as mock_connect:
        with patch("pandas.read_sql") as mock_read_sql:
            mock_read_sql.return_value = pd.DataFrame({"col": [1]})
            # Execute without limit
            result = execute_query_tool.invoke({"sql": "SELECT * FROM gold.sales"})
            
            # The sql guard should have passed it, and the executor should add LIMIT 100
            args, kwargs = mock_read_sql.call_args
            executed_sql = str(args[0])
            assert "LIMIT 100" in executed_sql.upper()
            assert "col" in result # It returns a markdown string of the dataframe

def test_execute_query_tool_blocks_drop_table():
    result = execute_query_tool.invoke({"sql": "DROP TABLE gold.sales"})
    assert "Error executing SQL: Forbidden keyword 'DROP' found in SQL." in result
