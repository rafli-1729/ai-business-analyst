"""
TrendAgent for trend and time-series analysis.

Specializes in:
- Temporal trends
- Seasonality detection
- Growth analysis
- Forecast-ready metrics
"""

from ai.agents.base.analytical_agent import AnalyticalAgent


class TrendAgent(AnalyticalAgent):
    """
    Agent for trend and temporal analysis.

    Priorities:
    - Temporal trends
    - Seasonality
    - Growth rates
    - Time-series decomposition
    """

    @property
    def name(self) -> str:
        return "trend"

    @property
    def primary_mart(self) -> str:
        return "temporal"

    @property
    def analytical_focus(self) -> list[str]:
        return [
            "temporal_trends",
            "seasonality",
            "growth_rates",
            "trend_direction",
        ]

    def build_system_prompt(self) -> str:
        """Build trend-focused system prompt."""
        return """
You are a temporal analytics expert specializing in trend and seasonality analysis.

Your role:
- Identify temporal trends and patterns
- Detect seasonality and cyclical patterns
- Calculate growth rates and momentum
- Forecast-ready metrics

Analytical priorities:
- What's the trend direction?
- Is there seasonality?
- What's the growth rate?
- What about momentum changes?

SQL style:
- Time-series grouping
- Window functions for trends
- Period-over-period comparisons
- Aggregation by time units

Generate PostgreSQL SQL that captures temporal patterns and trends.
""".strip()