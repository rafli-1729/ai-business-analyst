from core_analytics.agents.base import AgentArtifact, BaseAgent, run_direct_chain
from core_analytics.analytics.llm_client import LLMClient
from core_analytics.analytics.tools import _sql_executor
from core_analytics.semantic.loader import load_all_semantic_definitions
from typing import List
from pydantic import Field

class OperationsAgent(BaseAgent):
    llm_client: LLMClient = Field(default_factory=LLMClient)
    model_config = {"arbitrary_types_allowed": True}

    async def process(self, query: str) -> dict:
        llm = self.llm_client.get_llm()
        
        try:
            schema_context = load_all_semantic_definitions()
        except Exception:
            schema_context = "No semantic context available."
            
        enhanced_query = f"Please analyze this from a operations, logistics, or delivery perspective: {query}"
        
        return await run_direct_chain(
            query=enhanced_query,
            schema_context=schema_context,
            agent_name="Operations Agent",
            llm=llm,
            sql_executor=_sql_executor
        )

operations_agent_instance = OperationsAgent(name="ops_analyst", role="Operations Expert")
