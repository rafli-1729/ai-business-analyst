import logging
import json
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from core_analytics.agents.base import AgentState
from core_analytics.analytics.llm_client import LLMClient

# Import nodes
from core_analytics.agents.customer_agent import customer_agent_node

# Import legacy agents for temporary wrapping
from core_analytics.agents.sales_agent import sales_agent_instance
from core_analytics.agents.geography_agent import geography_agent_instance
from core_analytics.agents.product_agent import product_agent_instance
from core_analytics.agents.retention_agent import retention_agent_instance
from core_analytics.agents.trend_agent import trend_agent_instance
from core_analytics.agents.ranker_agent import ranker_agent_instance
from core_analytics.agents.diagnostic_agent import diagnostic_agent_instance
from core_analytics.agents.operations_agent import operations_agent_instance

logger = logging.getLogger(__name__)

# Legacy node wrappers
async def sales_node(state: AgentState): return {"artifacts": await sales_agent_instance.process(state["query"]), "active_agents": ["Sales Agent"]}
async def geo_node(state: AgentState): return {"artifacts": await geography_agent_instance.process(state["query"]), "active_agents": ["Geography Agent"]}
async def product_node(state: AgentState): return {"artifacts": await product_agent_instance.process(state["query"]), "active_agents": ["Product Agent"]}
async def retention_node(state: AgentState): return {"artifacts": await retention_agent_instance.process(state["query"]), "active_agents": ["Retention Agent"]}
async def trend_node(state: AgentState): return {"artifacts": await trend_agent_instance.process(state["query"]), "active_agents": ["Trend Agent"]}
async def ranker_node(state: AgentState): return {"artifacts": await ranker_agent_instance.process(state["query"]), "active_agents": ["Ranker Agent"]}
async def diagnostic_node(state: AgentState): return {"artifacts": await diagnostic_agent_instance.process(state["query"]), "active_agents": ["Diagnostic Agent"]}
async def ops_node(state: AgentState): return {"artifacts": await operations_agent_instance.process(state["query"]), "active_agents": ["Operations Agent"]}

def planner_node(state: AgentState):
    """Analyzes query and decides which domain agents to run."""
    llm = LLMClient().get_llm()
    
    try:
        with open("contracts/prompts/planner_prompt.txt", "r") as f:
            prompt_content = f.read()
    except Exception:
        prompt_content = "Return JSON array of tasks e.g. [{\"agent\": \"customer\", \"task\": \"analyze\"}] for query: {query}"
        
    system_prompt = prompt_content.replace("{query}", state["query"])
    
    response = llm.invoke([SystemMessage(content=system_prompt)])
    decomposition_json = response.content
    
    try:
        cleaned_json = decomposition_json.replace("```json", "").replace("```", "").strip()
        tasks_list = json.loads(cleaned_json)
        logger.info(f"Planner: Structured tasks: {tasks_list}")
    except Exception as e:
        logger.warning(f"Planner: Failed to parse task JSON: {e}. Defaulting to sales.")
        tasks_list = [{"task": "Default Sales Analysis", "agent": "sales"}]
        
    next_nodes = []
    valid_agents = ["sales", "geo", "customer", "product", "retention", "trend", "ranker", "diagnostic", "ops"]
    
    for item in tasks_list:
        agent_key = item.get("agent")
        if agent_key in valid_agents:
            next_nodes.append(agent_key)
            
    if not next_nodes:
        next_nodes = ["sales"]
        
    # Return exactly the destinations so the conditional edge can route to them in parallel
    return {"next": ",".join(next_nodes)}

def route_to_agents(state: AgentState):
    """Conditional edge router that returns a list of node names to execute in parallel"""
    destinations = state.get("next", "sales").split(",")
    # Deduplicate
    return list(set(destinations))

def synthesizer_node(state: AgentState):
    from core_analytics.agents.base import AgentArtifact
    
    summaries = [a.content for a in state.get("artifacts", []) if a.type == "executive_summary"]
    
    if not summaries:
        return {}
        
    if len(summaries) == 1:
        final_text = summaries[0]
    else:
        llm = LLMClient().get_llm()
        combined_text = "\n\n".join(f"- {s}" for s in summaries)
        prompt = f"You are the Lead Executive Analyst. Synthesize the following insights from various domain experts into EXACTLY ONE cohesive, punchy executive summary paragraph (max 4-5 sentences):\n\n{combined_text}"
        response = llm.invoke([SystemMessage(content=prompt)])
        final_text = response.content
        
    final_artifact = AgentArtifact(
        name="Executive Summary",
        type="unified_executive_summary",
        content=final_text
    )
    
    return {"artifacts": [final_artifact]}

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)
builder.add_node("customer", customer_agent_node)
builder.add_node("sales", sales_node)
builder.add_node("geo", geo_node)
builder.add_node("product", product_node)
builder.add_node("retention", retention_node)
builder.add_node("trend", trend_node)
builder.add_node("ranker", ranker_node)
builder.add_node("diagnostic", diagnostic_node)
builder.add_node("ops", ops_node)
builder.add_node("synthesizer", synthesizer_node)

builder.set_entry_point("planner")

# Add conditional edges to fan out to multiple agents based on planner's routing logic
builder.add_conditional_edges(
    "planner",
    route_to_agents,
    {
        "customer": "customer",
        "sales": "sales",
        "geo": "geo",
        "product": "product",
        "retention": "retention",
        "trend": "trend",
        "ranker": "ranker",
        "diagnostic": "diagnostic",
        "ops": "ops"
    }
)

# Fan in from all agents back to synthesizer, then to END
for node in ["customer", "sales", "geo", "product", "retention", "trend", "ranker", "diagnostic", "ops"]:
    builder.add_edge(node, "synthesizer")

builder.add_edge("synthesizer", END)

graph = builder.compile()

# Compatibility wrapper for existing application
class Planner:
    async def decompose_and_execute(self, query: str) -> dict:
        initial_state = {
            "query": query,
            "messages": [],
            "active_agents": [],
            "artifacts": [],
            "next": ""
        }
        
        # Invoke the LangGraph workflow
        final_state = await graph.ainvoke(initial_state)
        
        return {
            "artifacts": final_state.get("artifacts", []),
            "active_agents": final_state.get("active_agents", [])
        }

planner_instance = Planner()
