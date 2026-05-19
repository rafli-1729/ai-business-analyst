"""
Agent initialization and registration.

Initializes all specialized analytical agents in the registry.
This module centralizes agent registration to avoid scattered initialization.
"""

from core_analytics.agents.registry import register_agent
from core_analytics.agents.diagnostic_agent import diagnostic_agent_instance as DiagnosticAgent
from core_analytics.agents.trend_agent import trend_agent_instance as TrendAgent
from core_analytics.agents.ranker_agent import ranker_agent_instance as RankerAgent
from core_analytics.agents.sales_agent import sales_agent_instance as SalesAgent
from core_analytics.agents.geography_agent import geography_agent_instance as GeographyAgent
from core_analytics.agents.product_agent import product_agent_instance as ProductAgent
from core_analytics.agents.retention_agent import retention_agent_instance as RetentionAgent
from core_analytics.agents.operations_agent import operations_agent_instance as OperationsAgent
from core_analytics.agents.customer_agent import customer_agent_instance as CustomerAgent


def initialize_agents() -> None:
    """
    Initialize and register all analytical agents.

    Should be called during application startup.
    """
    register_agent(DiagnosticAgent)
    register_agent(TrendAgent)
    register_agent(RankerAgent)
    register_agent(SalesAgent)
    register_agent(GeographyAgent)
    register_agent(CustomerAgent)
    register_agent(RetentionAgent)
    register_agent(OperationsAgent)
    register_agent(ProductAgent)
