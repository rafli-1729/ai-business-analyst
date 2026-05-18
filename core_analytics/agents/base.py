from pydantic import BaseModel
from typing import List, Any, Optional, TypedDict
import operator
from typing import Annotated
import json
import logging

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

def parse_agent_response(response_content: str, agent_name: str) -> List[AgentArtifact]:
    """Helper to parse the JSON output from agents into unified artifacts."""
    artifacts = []
    
    try:
        # Try to find JSON block if wrapped in markdown
        cleaned = response_content
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0]
            
        data = json.loads(cleaned.strip())
        
        # 1. Executive Summary
        if data.get("executive_summary"):
            artifacts.append(AgentArtifact(
                name=f"{agent_name} Executive Summary",
                type="executive_summary",
                content=data["executive_summary"]
            ))
            
        # 2. Dashboard Explanation
        if data.get("dashboard_explanation"):
            artifacts.append(AgentArtifact(
                name=f"{agent_name} Dashboard Explanation",
                type="dashboard_explanation",
                content=data["dashboard_explanation"]
            ))
            
        # 3. Charts
        charts = data.get("charts", [])
        # Limit to max 2 charts
        for i, chart in enumerate(charts[:2]):
            artifacts.append(AgentArtifact(
                name=chart.get("title", f"{agent_name} Chart {i+1}"),
                type="chart",
                content=chart # Keep JSON payload for frontend
            ))
            
        # 4. Table (only if provided and usually if no charts)
        if data.get("table_markdown"):
            artifacts.append(AgentArtifact(
                name=f"{agent_name} Data Table",
                type="table",
                content=data["table_markdown"]
            ))
            
    except Exception as e:
        logger.error(f"Failed to parse agent JSON response: {e}. Fallback to plain text.")
        artifacts.append(AgentArtifact(
            name=f"{agent_name} Analysis",
            type="executive_summary",
            content=response_content
        ))
        
    return artifacts
