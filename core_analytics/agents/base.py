from pydantic import BaseModel
from typing import List, Any, Optional, TypedDict
import operator
from typing import Annotated

class AgentArtifact(BaseModel):
    name: str
    type: str  # e.g., 'executive_summary', 'dashboard_explanation', 'chart', 'table', 'sql'
    content: Any
    confidence: float = 1.0

# LangGraph State definition
class AgentState(TypedDict):
    query: str
    messages: Annotated[list, operator.add]
    active_agents: Annotated[list[str], operator.add]
    artifacts: Annotated[list[AgentArtifact], operator.add]
    next: str # For routing logic
