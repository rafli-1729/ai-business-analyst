from pydantic import BaseModel

class Agent(BaseModel):
    name: str
    role: str
    domain: str

planner = Agent(name="planner", role="Orchestrator", domain="general")
sales_agent = Agent(name="sales_agent", role="Sales Analyst", domain="sales")
