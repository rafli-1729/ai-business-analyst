"""
OperationsAgent for operational and efficiency analysis.

Specializes in:
- Order fulfillment
- Operational efficiency
- Seller performance
- Supply chain metrics
"""

from ai.agents.base.analytical_agent import AnalyticalAgent


class OperationsAgent(AnalyticalAgent):
    """
    Agent for operational and efficiency analysis.

    Priorities:
    - Order fulfillment
    - Operational efficiency
    - Seller performance
    - Supply chain metrics
    """

    @property
    def name(self) -> str:
        return "operations"

    @property
    def primary_mart(self) -> str:
        return "operations"

    @property
    def analytical_focus(self) -> list[str]:
        return [
            "order_fulfillment",
            "operational_efficiency",
            "seller_performance",
            "supply_chain_metrics",
            "quality_metrics",
        ]

    def build_system_prompt(self) -> str:
        """Build operations-focused system prompt."""
        return """
You are an operations analytics expert.

Your role:
- Monitor order fulfillment performance
- Measure operational efficiency
- Analyze seller performance
- Track supply chain health
- Identify bottlenecks

Analytical priorities:
- How's our fulfillment performing?
- What's our operational efficiency?
- Which sellers perform best?
- What's supply chain health?
- Where are bottlenecks?

SQL style:
- Order processing metrics
- Fulfillment time analysis
- Seller performance scorecards
- Quality and accuracy metrics
- Bottleneck identification

Generate PostgreSQL SQL that reveals operational performance and efficiency opportunities.
""".strip()
