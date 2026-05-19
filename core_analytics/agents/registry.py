from pydantic import BaseModel
from typing import Dict, Any, Type

class Agent(BaseModel):
    name: str
    role: str
    domain: str

# Registry to hold agent instances or classes
_agent_registry: Dict[str, Any] = {}

def register_agent(agent_obj: Any) -> None:
    """Register an agent instance or class."""
    name = getattr(agent_obj, "name", str(agent_obj))
    _agent_registry[name] = agent_obj

def get_agent(name: str) -> Any:
    """Get an agent by name."""
    return _agent_registry.get(name)

# Legacy / Default instances
planner = Agent(name="planner", role="Orchestrator", domain="general")
sales_agent = Agent(name="sales_agent", role="Sales Analyst", domain="sales")
