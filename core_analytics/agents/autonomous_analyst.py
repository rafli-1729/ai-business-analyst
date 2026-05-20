import json
import logging
from typing import List, Any

from langchain_core.messages import SystemMessage, ToolMessage, AIMessage
from langgraph.prebuilt import create_react_agent
import pandas as pd

from core_analytics.analytics.llm_client import LLMClient
from core_analytics.analytics.tools import list_tables_tool, describe_table_tool, execute_query_tool, sample_table_tool, _executor
from core_analytics.agents.base import AgentArtifact
from core_analytics.visualization.charts import infer_chart_type, prepare_chart_data

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Autonomous Data Analyst in a live DB. Answer via schema introspection and SELECT queries.

1. LANGUAGE: Final response, summary, and reasoning MUST be in ENGLISH.
2. LOOP: list_warehouse_tables -> describe_warehouse_table -> sample_warehouse_table (mandatory for categorical values) -> execute_analytical_query.
3. VISUALIZATION: 
- ALWAYS determine the best visualization for EVERY relevant data finding.
- If you execute multiple queries, you can provide multiple chart configurations.
- Use `[CHART_CONFIG]` followed by a JSON object.
- Config: `{"type": "bar"|"line"|"area"|"pie"|"dual_axis", "xAxisKey": "col_name", "yAxisKey": ["col1", "col2"], "title": "Chart Title"}`
- SPECIAL: Use `dual_axis` for mixed scales (e.g., 'Orders' vs 'Revenue'). The first column in `yAxisKey` will be a BAR on the LEFT axis, the rest will be LINES on the RIGHT axis.
- Recommend 'line'/'area' for temporal data, 'bar'/'pie' for categorical.
4. SYNTHESIZE: 
- Provide a HIGH-DENSITY, multi-paragraph analytical summary.
- Focus on describing business impacts, month-over-month trends, and specific data observations.
- Be comprehensive: if the data shows growth, explain the magnitude; if there are anomalies, hypothesize the cause based on the results.
- End response immediately after the last insight. NO chitchat/filler.
- Avoid: Use plain text for numbers and metrics instead of mathematical equations.
"""

class AutonomousAnalyst:
    def __init__(self):
        self.llm_client = LLMClient()
        self.llm = self.llm_client.get_llm()
        self.tools = [list_tables_tool, describe_table_tool, execute_query_tool, sample_table_tool]
        
        # Create LangGraph ReAct agent
        self.agent_executor = create_react_agent(
            model=self.llm,
            tools=self.tools
        )

    async def run(self, user_query: str) -> dict:
        """
        Executes the ReAct loop and returns artifacts for the API.
        """
        logger.info(f"Autonomous Analyst starting for query: {user_query}")
        
        # 0. Clear session cache to avoid stale results
        _executor.clear_cache()

        inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", user_query)]}
        
        # Track all messages for artifact extraction at the end
        all_messages = []
        
        # Use "updates" mode to only get NEW chunks, reducing processing overhead
        async for chunk in self.agent_executor.astream(inputs, stream_mode="updates"):
            for node_name, updates in chunk.items():
                new_messages = updates.get("messages", [])
                for msg in new_messages:
                    all_messages.append(msg)
                    if isinstance(msg, AIMessage):
                        if msg.content:
                            thought = msg.content.split("\n")[0]
                            logger.info(f"Agent Thought: {thought}...")
                        if msg.tool_calls:
                            for tc in msg.tool_calls:
                                logger.info(f"Agent Action: Calling tool '{tc['name']}'")

        final_response = all_messages[-1].content if all_messages else "No response generated."
        
        # Extract ALL custom chart configs from agent response
        custom_chart_configs = []
        if "[CHART_CONFIG]" in final_response:
            try:
                parts = final_response.split("[CHART_CONFIG]")
                # The first part is the narrative text
                final_response = parts[0].strip()
                # The rest are config blocks
                for config_part in parts[1:]:
                    config_str = config_part.strip()
                    if "}" in config_str:
                        config_str = config_str[:config_str.find("}")+1]
                    try:
                        custom_chart_configs.append(json.loads(config_str))
                    except:
                        continue
            except Exception as e:
                logger.error(f"Failed to parse custom chart configs: {e}")

        artifacts = []
        captured_tables = []
        last_sql = None
        
        # Extract executed SQL results from the session cache
        for msg in all_messages:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    if tool_call["name"] == "execute_analytical_query":
                        sql = tool_call["args"].get("sql", "")
                        if sql:
                            last_sql = sql
                            df = _executor.result_cache.get(sql.strip())
                            if df is not None and not df.empty:
                                captured_tables.append(df.to_dict(orient="records"))

        # 1. Executive Summary Artifact
        artifacts.append(AgentArtifact(
            name="Analysis Summary",
            type="executive_summary",
            content=final_response
        ))
        
        # 2. Add all captured tables as separate artifacts
        for i, table_records in enumerate(captured_tables):
            artifacts.append(AgentArtifact(
                name=f"Data Matrix {i+1}" if len(captured_tables) > 1 else "Data Matrix",
                type="table",
                content=table_records
            ))
            
            # 3. Chart Artifact using upgraded visualization logic
            # Map configurations to tables by index
            specific_config = custom_chart_configs[i] if i < len(custom_chart_configs) else None
            df_for_chart = pd.DataFrame(table_records)
            chart_spec = prepare_chart_data(df_for_chart, custom_config=specific_config)

            if chart_spec:
                artifacts.append(AgentArtifact(
                    name=f"Visualization {i+1}" if len(captured_tables) > 1 else "Visualization",
                    type="chart",
                    content=chart_spec
                ))

        artifacts.append(AgentArtifact(
            name="Generated SQL",
            type="sql",
            content=last_sql if last_sql else "-- No SQL was executed"
        ))
        
        return {
            "artifacts": artifacts,
            "active_agents": ["AutonomousAnalyst"]
        }

autonomous_analyst_instance = AutonomousAnalyst()
