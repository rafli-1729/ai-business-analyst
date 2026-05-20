import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, HumanMessage
from core_analytics.agents.autonomous_analyst import autonomous_analyst_instance

@pytest.mark.asyncio
async def test_autonomous_analyst_run_extracts_sql_and_synthesizes_artifacts():
    # Mock the ainvoke method to return a predefined message history
    mock_messages = [
        HumanMessage(content="What are the total sales?"),
        AIMessage(content="", tool_calls=[
            {"name": "list_warehouse_tables", "args": {"schemas": ["gold"]}, "id": "call_1"}
        ]),
        # ... intermediate steps ...
        AIMessage(content="", tool_calls=[
            {"name": "execute_analytical_query", "args": {"sql": "SELECT SUM(price) FROM gold.sales"}, "id": "call_2"}
        ]),
        AIMessage(content="The total sales are 1000.")
    ]
    
    with patch("core_analytics.agents.autonomous_analyst.autonomous_analyst_instance.agent_executor.ainvoke") as mock_ainvoke:
        mock_ainvoke.return_value = {"messages": mock_messages}
        
        with patch("core_analytics.agents.autonomous_analyst._executor.engine.connect") as mock_connect:
            with patch("pandas.read_sql") as mock_read_sql:
                import pandas as pd
                mock_read_sql.return_value = pd.DataFrame({"total_sales": [1000]})
                
                result = await autonomous_analyst_instance.run("What are the total sales?")
                
                artifacts = result.get("artifacts", [])
                
                # Verify we got artifacts
                assert len(artifacts) >= 3
                
                # Check Summary
                summary = next(a for a in artifacts if a.type == "executive_summary")
                assert summary.content == "The total sales are 1000."
                
                # Check Table Data
                table = next(a for a in artifacts if a.type == "table")
                assert table.content == [{"total_sales": 1000}]
                
                # Check SQL extraction
                sql = next(a for a in artifacts if a.type == "sql")
                assert "SELECT SUM(price) FROM gold.sales" in sql.content

@pytest.mark.asyncio
async def test_autonomous_analyst_graceful_failure():
    # Test when no tool calls are made
    mock_messages = [
        HumanMessage(content="Hello"),
        AIMessage(content="I am an AI, how can I help?")
    ]
    
    with patch("core_analytics.agents.autonomous_analyst.autonomous_analyst_instance.agent_executor.ainvoke") as mock_ainvoke:
        mock_ainvoke.return_value = {"messages": mock_messages}
        
        result = await autonomous_analyst_instance.run("Hello")
        artifacts = result.get("artifacts", [])
        
        summary = next(a for a in artifacts if a.type == "executive_summary")
        assert summary.content == "I am an AI, how can I help?"
        
        sql = next(a for a in artifacts if a.type == "sql")
        assert sql.content == "-- No SQL was executed"
