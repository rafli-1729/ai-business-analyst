import logging
import json
import time
import re
import pandas as pd
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from core_analytics.agents.base import AgentState
from core_analytics.analytics.llm_client import LLMClient

# Import nodes
from core_analytics.agents.customer_agent import customer_agent_instance

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
async def planner_node(state: AgentState):
    """Decomposes query into tasks and assigns each to a specific agent."""
    from core_analytics.orchestration.intent_classifier import classify_intent_by_keywords
    from core_analytics.semantic.loader import load_all_semantic_definitions
    
    start_time = time.time()
    query = state["query"]
    
    # Load semantic context to help planner understand entities (city, state, etc)
    try:
        schema_context = load_all_semantic_definitions()
    except Exception:
        schema_context = "No semantic context available."

    # 1. Decompose into tasks using LLM
    llm = LLMClient().get_llm()
    try:
        with open("contracts/prompts/planner_prompt.txt", "r") as f:
            prompt_template = f.read()
        system_prompt = prompt_template.format(query=query)
        # Add schema context as a second system instruction or append to prompt
        system_prompt += f"\n\nSCHEMA CONTEXT:\n{schema_context}"
    except Exception:
        system_prompt = f"Decompose this query into 1-2 distinct analytical tasks using <task> tags: {query}"
        
    response = await llm.ainvoke([SystemMessage(content=system_prompt)])
    planner_output = response.content
    
    import re
    tasks = re.findall(r'<task>(.*?)</task>', planner_output, re.DOTALL | re.IGNORECASE)
    
    if not tasks:
        logger.warning(f"Planner: Failed to parse tasks. Defaulting to original query as one task.")
        tasks = [query]

    # 2. Map each task to an agent using keywords
    next_assignments = []
    
    for task_text in tasks[:2]: # Limit to max 2 tasks for layout
        agent_key = classify_intent_by_keywords(task_text)
        if not agent_key:
            # Fallback for task-specific mapping if generic keywords fail
            agent_key = "sales" 
        
        next_assignments.append(f"{agent_key}:{task_text.strip()}")

    duration = (time.time() - start_time) * 1000
    logger.info(f"Planner: Decomposed into {len(next_assignments)} tasks in {duration:.2f}ms")
    for task in tasks:
        logger.info(f"Planner Task: {task.strip()}")
    
    return {"next": "|".join(next_assignments)}

def route_to_agents(state: AgentState):
    """Routes to multiple agent nodes based on task assignments."""
    assignments = state.get("next", "sales:").split("|")
    destinations = []
    for ass in assignments:
        if ":" in ass:
            agent_node = ass.split(":")[0]
            destinations.append(agent_node)
    return list(set(destinations)) if destinations else ["sales"]

# Updated node wrappers to use assigned task instead of global query
async def task_node_wrapper(state: AgentState, agent_instance, agent_name: str):
    # Find the task assigned to THIS agent from state["next"]
    assignments = state.get("next", "").split("|")
    my_task = state["query"] # Default
    
    agent_key = agent_name.lower().split(" ")[0]
    if agent_key == "geography": agent_key = "geo"
    
    for ass in assignments:
        if ":" in ass:
            prefix, task_text = ass.split(":", 1)
            if prefix == agent_key:
                my_task = task_text
                break
            
    result = await agent_instance.process(my_task)
    return {"artifacts": result.get("artifacts", []), "active_agents": [agent_name]}

async def customer_node(state: AgentState): return await task_node_wrapper(state, customer_agent_instance, "Customer Agent")
async def sales_node(state: AgentState): return await task_node_wrapper(state, sales_agent_instance, "Sales Agent")
async def geo_node(state: AgentState): return await task_node_wrapper(state, geography_agent_instance, "Geography Agent")
async def product_node(state: AgentState): return await task_node_wrapper(state, product_agent_instance, "Product Agent")
async def retention_node(state: AgentState): return await task_node_wrapper(state, retention_agent_instance, "Retention Agent")
async def trend_node(state: AgentState): return await task_node_wrapper(state, trend_agent_instance, "Trend Agent")
async def ranker_node(state: AgentState): return await task_node_wrapper(state, ranker_agent_instance, "Ranker Agent")
async def diagnostic_node(state: AgentState): return await task_node_wrapper(state, diagnostic_agent_instance, "Diagnostic Agent")
async def ops_node(state: AgentState): return await task_node_wrapper(state, operations_agent_instance, "Operations Agent")

def synthesizer_node(state: AgentState):
    from core_analytics.agents.base import AgentArtifact
    import pandas as pd
    
    # IMPORTANT: Do not return unique_artifacts here, as they are already in the state.
    # We only return the NEW unified summary.
    all_artifacts = state.get("artifacts", [])
    
    summaries = [a.content for a in all_artifacts if a.type == "executive_summary"]
    raw_data_artifacts = [a for a in all_artifacts if a.type == "raw_data"]
    
    if not summaries:
        return {}
        
    # 1. Synthesize Text (No emoticons rule)
    llm = LLMClient().get_llm()
    if len(summaries) == 1:
        prompt = f"Rewrite the following business insight into EXACTLY ONE cohesive, punchy executive summary paragraph (MAX 50 WORDS). STRICT RULES: 1. DO NOT use any emoticons or emojis. 2. DO NOT include any titles like 'Executive Summary'. 3. Maintain a professional, executive tone.\n\n{summaries[0]}"
    else:
        combined_text = "\n\n".join(f"- {s}" for s in summaries)
        prompt = f"Synthesize the following insights into EXACTLY ONE cohesive, punchy executive summary paragraph (MAX 50 WORDS). STRICT RULES: 1. DO NOT use any emoticons or emojis. 2. DO NOT include any titles like 'Executive Summary'. 3. Maintain a professional, executive tone.\n\n{combined_text}"
    
    response = llm.invoke([SystemMessage(content=prompt)])
    final_text = response.content

    # 2. Append Data Preview Table (Max 5 rows)
    if raw_data_artifacts:
        df = pd.DataFrame(raw_data_artifacts[0].content)
        if not df.empty:
            # Create a copy to avoid SettingWithCopyWarning
            preview_df = df.head(5).copy()
            cols_to_show = [c for c in preview_df.columns if not any(x in c.lower() for x in ['id', 'key', 'uuid', '_at'])]
            if not cols_to_show: cols_to_show = preview_df.columns[:min(4, len(preview_df.columns))]
            
            # Format numbers in the table preview
            for col in preview_df.columns:
                if pd.api.types.is_numeric_dtype(preview_df[col]):
                    # Cast to object first to avoid FutureWarning
                    preview_df[col] = preview_df[col].astype(object)
                    preview_df.loc[:, col] = preview_df[col].map(lambda x: f"{x:,.2f}" if isinstance(x, float) else f"{x:,}")
            
            table_md = "\n\n**Key Data Preview:**\n" + preview_df[cols_to_show].to_markdown(index=False)
            final_text += table_md
        else:
            final_text += "\n\n*No preview data available for this query.*"
    elif not any(a.type == "chart" for a in all_artifacts):
        final_text += "\n\n*Insight generated based on conceptual reasoning (no direct data points found).* "
        
    final_artifact = AgentArtifact(
        name="Executive Summary",
        type="unified_executive_summary",
        content=final_text
    )
    
    # Return ONLY the new artifact to avoid duplication due to operator.add
    return {"artifacts": [final_artifact]}

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)
builder.add_node("customer", customer_node)
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
        
        # FINAL GLOBAL DEDUPLICATION before returning to UI
        all_artifacts = final_state.get("artifacts", [])
        unique_artifacts = []
        seen_charts = set()
        seen_exps = set()
        
        # Check if we have a unified summary
        has_unified = any(a.type == "unified_executive_summary" for a in all_artifacts)
        
        for art in all_artifacts:
            # Skip individual summaries if a unified one exists
            if art.type == "executive_summary" and has_unified:
                continue
                
            if art.type == "chart":
                title = art.content.get("title", "").strip().lower()
                if title not in seen_charts:
                    unique_artifacts.append(art)
                    seen_charts.add(title)
            elif art.type == "dashboard_explanation":
                # Robust content-based deduplication
                snippet = re.sub(r'\W+', '', str(art.content)).lower()[:150]
                if snippet not in seen_exps:
                    unique_artifacts.append(art)
                    seen_exps.add(snippet)
            elif art.type == "unified_executive_summary":
                # Keep only the last one (should only be one anyway)
                unique_artifacts = [a for a in unique_artifacts if a.type != "unified_executive_summary"]
                unique_artifacts.append(art)
            else:
                # Keep raw_data and other non-visual artifacts
                unique_artifacts.append(art)
        
        return {
            "artifacts": unique_artifacts,
            "active_agents": final_state.get("active_agents", [])
        }

planner_instance = Planner()
