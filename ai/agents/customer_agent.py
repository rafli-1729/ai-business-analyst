"""
CustomerAgent for customer analysis.

Specializes in:
- Customer segments
- Customer value
- Purchase patterns
- Customer demographics
"""

from ai.agents.base.analytical_agent import AnalyticalAgent


class CustomerAgent(AnalyticalAgent):
    """
    Agent for customer analysis.

    Priorities:
    - Customer segments
    - Customer lifetime value
    - Purchase patterns
    - Customer demographics
    """

    @property
    def name(self) -> str:
        return "customer"

    @property
    def primary_mart(self) -> str:
        return "customers"

    @property
    def analytical_focus(self) -> list[str]:
        return [
            "customer_segments",
            "customer_value",
            "purchase_patterns",
            "customer_demographics",
            "behavior_analysis",
        ]

    def build_system_prompt(self) -> str:
        """Build customer-focused system prompt."""
        return """
            You are a customer analytics expert.

            Your role:
            - Segment customers by characteristics
            - Calculate customer lifetime value
            - Analyze purchase behavior patterns
            - Understand customer demographics
            - Identify high-value customers

            Analytical priorities:
            - How do we segment customers?
            - What's customer lifetime value?
            - What are purchase patterns?
            - Who are our best customers?
            - What drives customer behavior?

            SQL style:
            - Customer segmentation
            - RFM (Recency, Frequency, Monetary) analysis
            - Cohort-based analysis
            - Customer demographics
            - Behavioral metrics

            Generate PostgreSQL SQL that segments customers and reveals behavioral patterns.
            """.strip()
