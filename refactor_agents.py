import glob
import os

template = """from core_analytics.agents.base import AgentArtifact, BaseAgent, run_direct_chain
from core_analytics.analytics.llm_client import LLMClient
from core_analytics.analytics.tools import _sql_executor
from core_analytics.semantic.loader import load_all_semantic_definitions
from domains.{domain_folder}.metadata import get_{domain_name}_context
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
            
        try:
            domain_context = get_{domain_name}_context()
            schema_context += f"\\n\\n{{domain_context}}"
        except Exception:
            pass
        
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
    ("customer", "customers", "customer", "CustomerAgent", "Customer Agent", "customer_analyst", "Customer Expert", "customer_agent_instance"),
    ("geography", "geography", "geography", "GeographyAgent", "Geography Agent", "geo_analyst", "Geography Expert", "geography_agent_instance"),
    ("product", "products", "product", "ProductAgent", "Product Agent", "product_analyst", "Product Expert", "product_agent_instance"),
]

for agent in agents:
    prefix, domain_folder, domain_name, class_name, class_name_str, agent_name_id, role, instance_name = agent
    content = template.format(
        domain_folder=domain_folder,
        domain_name=domain_name,
        class_name=class_name,
        domain_desc=domain_name,
        class_name_str=class_name_str,
        agent_name_id=agent_name_id,
        role=role,
        instance_name=instance_name
    )
    with open(f"core_analytics/agents/{prefix}_agent.py", "w") as f:
        f.write(content)
