from pydantic import BaseModel
from typing import List, Any, Optional, TypedDict
import operator
from typing import Annotated
import json
import logging
import re
import time
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

class AgentArtifact(BaseModel):
    name: str
    type: str  # e.g., 'executive_summary', 'dashboard_explanation', 'chart', 'table'
    content: Any
    confidence: float = 1.0

# LangGraph State definition
class AgentState(TypedDict):
    query: str
    messages: Annotated[list, operator.add]
    active_agents: Annotated[list[str], operator.add]
    artifacts: Annotated[list[AgentArtifact], operator.add]
    next: str # For routing logic

class BaseAgent(BaseModel):
    name: str
    role: str
    
    def process(self, query: str) -> AgentArtifact:
        raise NotImplementedError("Subclasses must implement process method")

def parse_agent_response(response_content: str, agent_name: str, df_records: list = None) -> List[AgentArtifact]:
    """Helper to parse the JSON output from agents into unified artifacts."""
    artifacts = []
    
    # Sanitize df_records once at the start for JSON compliance (NaN/Inf -> null)
    sanitized_records = None
    if df_records is not None:
        import math
        sanitized_records = []
        for record in df_records:
            sanitized_row = {}
            for k, v in record.items():
                try:
                    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                        sanitized_row[k] = None
                    else:
                        sanitized_row[k] = v
                except Exception:
                    sanitized_row[k] = None
            sanitized_records.append(sanitized_row)

    try:
        import re
        import json
        
        # 1. Robust JSON Extraction
        json_str = response_content
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_content, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1).strip()
        else:
            # Fallback: extract everything between the first { and last }
            start = response_content.find('{')
            end = response_content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response_content[start:end]
                
        # 2. Cleanup trailing commas often left by LLMs
        json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
        
        data = json.loads(json_str, strict=False)
        
        # 3. Build Artifacts
        if data.get("executive_summary"):
            artifacts.append(AgentArtifact(
                name=f"{agent_name} Executive Summary",
                type="executive_summary",
                content=data["executive_summary"]
            ))
            
        exps = data.get("dashboard_explanations", [])
        if isinstance(exps, str): exps = [exps]
        for i, exp in enumerate(exps[:1]): # Limit to 1 explanation per task
            artifacts.append(AgentArtifact(
                name=f"{agent_name} Interpretation {i+1}",
                type="dashboard_explanation",
                content=exp
            ))
            
        charts = data.get("charts", [])
        if isinstance(charts, dict): charts = [charts]
        
        for i, chart_spec in enumerate(charts[:1]): # Limit to 1 chart per task
            if chart_spec and isinstance(chart_spec, dict) and sanitized_records:
                chart_spec["data"] = sanitized_records
                artifacts.append(AgentArtifact(
                    name=chart_spec.get("title", f"{agent_name} Chart {i+1}"),
                    type="chart",
                    content=chart_spec
                ))
            
    except Exception as e:
        logger.error(f"Failed to parse agent response: {e}. Raw content: {response_content[:200]}")
        artifacts.append(AgentArtifact(
            name=f"{agent_name} Analysis",
            type="executive_summary",
            content=response_content
        ))
        
    # Always append the raw data for download if available
    if sanitized_records is not None:
        artifacts.append(AgentArtifact(
            name=f"{agent_name} Raw Data",
            type="raw_data",
            content=sanitized_records
        ))
        
    return artifacts

async def run_direct_chain(query: str, schema_context: str, agent_name: str, llm, sql_executor, skill_context: str = "") -> dict:
    """Runs a direct 2-step chain (LLM -> SQL -> LLM) instead of ReAct loop for massive latency reduction."""
    
    start_total = time.time()
    # --- Step 1: SQL Generation ---
    t1 = time.time()
    try:
        with open("contracts/prompts/sql_generation.txt", "r") as f:
            sql_prompt_template = f.read()
        sql_system_prompt = sql_prompt_template.format(schema_context=schema_context, query=query)
    except Exception:
        sql_system_prompt = f"Write a raw PostgreSQL SELECT query for: {query}\nSchema:\n{schema_context}\nReturn ONLY the raw SQL."

    if skill_context:
        sql_system_prompt += f"\n\nAGENT PERSONA / SKILL INSTRUCTIONS:\n{skill_context}"

    sql_response = await llm.ainvoke([SystemMessage(content=sql_system_prompt)])
    sql_query_raw = sql_response.content
    
    # Extract from <sql> tags
    sql_match = re.search(r'<sql>(.*?)</sql>', sql_query_raw, re.DOTALL | re.IGNORECASE)
    if sql_match:
        sql_query = sql_match.group(1).strip()
    else:
        sql_query = sql_query_raw.replace("```sql", "").replace("```", "").strip()
    
    duration_sql_gen = (time.time() - t1) * 1000
    logger.info(f"Agent [{agent_name}]: SQL generation took {duration_sql_gen:.2f}ms")

    df_records = None
    # --- Step 2: SQL Execution ---
    t2 = time.time()
    try:
        df = sql_executor.execute(sql_query)
        data_str = df.head(50).to_string() # Limit rows to avoid context overflow
        df_records = df.head(1000).to_dict(orient='records') # Allow up to 1000 rows for CSV download
    except Exception as e:
        data_str = f"Error executing SQL: {e}"
        sql_query = f"-- {sql_query}\n-- Execution failed"
    
    duration_sql_exec = (time.time() - t2) * 1000
    logger.info(f"Agent [{agent_name}]: SQL execution took {duration_sql_exec:.2f}ms")

    # --- Step 3: Insight Generation ---
    t3 = time.time()
    try:
        with open("contracts/prompts/insight_generation.txt", "r") as f:
            insight_prompt_template = f.read()
        insight_system_prompt = insight_prompt_template.format(query=query, sql=sql_query, data=data_str)
    except Exception:
        insight_system_prompt = f"Generate JSON insights for query: {query}\nData:\n{data_str}"
        
    insight_response = await llm.ainvoke([SystemMessage(content=insight_system_prompt)])
    
    duration_insight = (time.time() - t3) * 1000
    logger.info(f"Agent [{agent_name}]: Insight generation took {duration_insight:.2f}ms")

    artifacts = parse_agent_response(insight_response.content, agent_name, df_records=df_records)
    
    # If the SQL failed, add an error artifact
    if "Error executing SQL" in data_str:
        artifacts.append(AgentArtifact(
            name=f"{agent_name} SQL Error",
            type="executive_summary",
            content=f"Failed to retrieve data. The generated SQL was invalid: {data_str}"
        ))
    
    total_duration = (time.time() - start_total) * 1000
    logger.info(f"Agent [{agent_name}]: Total chain completed in {total_duration:.2f}ms")
        
    return {
        "artifacts": artifacts,
        "active_agents": [agent_name]
    }
