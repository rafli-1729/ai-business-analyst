"""
Agent initialization and registration.

Initializes all specialized analytical agents in the registry.
This module centralizes agent registration to avoid scattered initialization.
"""

from ai.registries.agent_registry import register_agent
from ai.agents.diagnostic_agent import DiagnosticAgent
from ai.agents.trend_agent import TrendAgent
from ai.agents.ranker_agent import RankerAgent
from ai.agents.sales_agent import SalesAgent
from ai.agents.geography_agent import GeographyAgent
from ai.agents.customer_agent import CustomerAgent
from ai.agents.retention_agent import RetentionAgent
from ai.agents.operations_agent import OperationsAgent


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
