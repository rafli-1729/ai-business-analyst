from core_analytics.agents.base import AgentState, AgentArtifact, BaseAgent, parse_agent_response
from core_analytics.analytics.llm_client import LLMClient
from core_analytics.analytics.tools import execute_sql_tool
from core_analytics.semantic.loader import load_all_semantic_definitions
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from typing import List

def sales_agent_node(state: AgentState):
    """LangGraph node function for Sales Agent"""
    llm = LLMClient().get_llm()
    tools = [execute_sql_tool]
    agent = create_react_agent(llm, tools)
    
    try:
        schema_context = load_all_semantic_definitions()
    except Exception:
        schema_context = "No semantic context available."
    
    try:
        with open("contracts/prompts/base_sql_prompt.txt", "r") as f:
            prompt_template = f.read()
        system_prompt = prompt_template.format(schema_context=schema_context, query="")
    except Exception:
        system_prompt = "You are a sales domain expert. Use the execute_sql_tool to query the database."
    
    response = agent.invoke({
        "messages": [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Please analyze this from a sales and revenue perspective: {state['query']}")
        ]
    })
    
    # Sales creates an executive summary artifact
    artifacts = parse_agent_response(response["messages"][-1].content, "Sales Agent")
    return {"artifacts": artifacts, "active_agents": ["Sales Agent"]}

# Keep old class format for backward compatibility
from core_analytics.analytics.tools import ExecuteSQLTool
from pydantic import Field

class SalesAgent(BaseAgent):
    llm: LLMClient = Field(default_factory=LLMClient)
    sql_tool: ExecuteSQLTool = Field(default_factory=ExecuteSQLTool)
    model_config = {"arbitrary_types_allowed": True}

    async def process(self, query: str) -> List[AgentArtifact]:
        state = AgentState(query=query, messages=[], active_agents=[], artifacts=[], next="")
        return sales_agent_node(state)["artifacts"]

sales_agent_instance = SalesAgent(name="sales_analyst", role="Sales Expert")
