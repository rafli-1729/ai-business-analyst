"""
SalesAgent for sales and revenue analysis.

Specializes in:
- Revenue metrics
- Growth rates
- Average order value
- Sales trends and seasonality
"""

from ai.agents.base.analytical_agent import AnalyticalAgent


class SalesAgent(AnalyticalAgent):
    """
    Agent for sales and revenue analysis.

    Priorities:
    - Revenue
    - Growth rates
    - AOV (Average Order Value)
    - Seasonality
    - Explainable aggregation
    """

    @property
    def name(self) -> str:
        return "sales"

    @property
    def primary_mart(self) -> str:
        return "sales"

    @property
    def analytical_focus(self) -> list[str]:
        return [
            "revenue",
            "growth_rates",
            "average_order_value",
            "seasonality",
            "explainable_aggregation",
        ]

    def build_system_prompt(self) -> str:
        """Build sales-focused system prompt."""
        return """
You are a sales analytics expert.

Your role:
- Analyze revenue metrics and trends
- Calculate growth rates and YoY comparisons
- Measure average order value and ticket size
- Detect seasonal patterns in sales
- Explain sales drivers and factors

Analytical priorities:
- What are our revenue trends?
- What's driving growth or decline?
- How does AOV trend over time?
- What seasonality patterns exist?
- Which segments drive revenue?

SQL style:
- Revenue aggregations by period
- Period-over-period comparisons
- Segment-based analysis
- Clear, business-friendly naming
- Explainable breakdowns

Generate PostgreSQL SQL that tells a clear revenue story with supporting details.
""".strip()
