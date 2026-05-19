from core_analytics.agents.base import AgentArtifact, BaseAgent, run_direct_chain
from core_analytics.analytics.llm_client import LLMClient
from core_analytics.analytics.tools import _sql_executor
from core_analytics.semantic.loader import load_all_semantic_definitions
from domains.sales.metadata import get_sales_context
from typing import List
from pydantic import Field

class SalesAgent(BaseAgent):
    llm_client: LLMClient = Field(default_factory=LLMClient)
    model_config = {"arbitrary_types_allowed": True}

    async def process(self, query: str) -> dict:
        llm = self.llm_client.get_llm()
        
        try:
            schema_context = load_all_semantic_definitions()
        except Exception:
            schema_context = "No semantic context available."
            
        try:
            sales_context = get_sales_context()
            schema_context += f"\n\n{sales_context}"
        except Exception:
            pass
            
        skill_context = ""
        import os
        skill_path = "skills/sales_agent.md"
        if os.path.exists(skill_path):
            with open(skill_path, "r") as f:
                skill_context = f.read()
        
        enhanced_query = f"Please analyze this from a sales and revenue perspective: {query}"
        
        return await run_direct_chain(
            query=enhanced_query,
            schema_context=schema_context,
            agent_name="Sales Agent",
            llm=llm,
            sql_executor=_sql_executor,
            skill_context=skill_context
        )

sales_agent_instance = SalesAgent(name="sales_analyst", role="Sales Expert")
