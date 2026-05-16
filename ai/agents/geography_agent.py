"""
GeographyAgent for geographic and regional analysis.

Specializes in:
- Regional comparisons
- State/city performance
- Delivery analysis
- Geographic concentration
"""

from ai.agents.base.analytical_agent import AnalyticalAgent


class GeographyAgent(AnalyticalAgent):
    """
    Agent for geographic and regional analysis.

    Priorities:
    - Regional comparisons
    - State and city performance
    - Delivery analysis
    - Geographic concentration
    """

    @property
    def name(self) -> str:
        return "geography"

    @property
    def primary_mart(self) -> str:
        return "geography"

    @property
    def analytical_focus(self) -> list[str]:
        return [
            "regional_comparisons",
            "state_performance",
            "city_performance",
            "delivery_analysis",
            "geographic_concentration",
        ]

    def build_system_prompt(self) -> str:
        """Build geography-focused system prompt."""
        return """
You are a geographic analytics expert.

Your role:
- Compare performance across regions
- Analyze state and city-level metrics
- Evaluate delivery performance by location
- Identify geographic concentration
- Highlight regional disparities

Analytical priorities:
- Which regions perform best?
- What are state/city rankings?
- How does delivery vary by location?
- Where is our business concentrated?
- What are regional growth rates?

SQL style:
- Geographic grouping (state, city)
- Regional performance comparisons
- Delivery metrics by location
- Market penetration analysis
- Geographic heatmaps data

Generate PostgreSQL SQL that provides geographic insights and regional patterns.
""".strip()
