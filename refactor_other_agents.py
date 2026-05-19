import glob
import os

template = """from core_analytics.agents.base import AgentArtifact, BaseAgent, run_direct_chain
from core_analytics.analytics.llm_client import LLMClient
from core_analytics.analytics.tools import _sql_executor
from core_analytics.semantic.loader import load_all_semantic_definitions
from typing import List
from pydantic import Field

class {class_name}(BaseAgent):
    llm_client: LLMClient = Field(default_factory=LLMClient)
    model_config = {{"arbitrary_types_allowed": True}}

    async def process(self, query: str) -> dict:
        llm = self.llm_client.get_llm()
        
        try:
            schema_context = load_all_semantic_definitions()
        except Exception:
            schema_context = "No semantic context available."
            
        enhanced_query = f"Please analyze this from a {domain_desc} perspective: {{query}}"
        
        return await run_direct_chain(
            query=enhanced_query,
            schema_context=schema_context,
            agent_name="{class_name_str}",
            llm=llm,
            sql_executor=_sql_executor
        )

{instance_name} = {class_name}(name="{agent_name_id}", role="{role}")
"""

agents = [
    ("retention", "RetentionAgent", "Retention Agent", "retention and churn", "retention_analyst", "Retention Expert", "retention_agent_instance"),
    ("trend", "TrendAgent", "Trend Agent", "time-series and trend", "trend_analyst", "Trend Expert", "trend_agent_instance"),
    ("ranker", "RankerAgent", "Ranker Agent", "ranking and comparison", "ranker_analyst", "Ranking Expert", "ranker_agent_instance"),
    ("diagnostic", "DiagnosticAgent", "Diagnostic Agent", "diagnostic and root-cause", "diagnostic_analyst", "Diagnostic Expert", "diagnostic_agent_instance"),
    ("operations", "OperationsAgent", "Operations Agent", "operations, logistics, or delivery", "ops_analyst", "Operations Expert", "operations_agent_instance"),
]

for agent in agents:
    prefix, class_name, class_name_str, domain_desc, agent_name_id, role, instance_name = agent
    content = template.format(
        class_name=class_name,
        domain_desc=domain_desc,
        class_name_str=class_name_str,
        agent_name_id=agent_name_id,
        role=role,
        instance_name=instance_name
    )
    with open(f"core_analytics/agents/{prefix}_agent.py", "w") as f:
        f.write(content)
