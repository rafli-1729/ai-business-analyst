"""
RankerAgent for ranking and aggregation analysis.

Specializes in:
- Top N rankings
- Comparative rankings
- Group aggregations
"""

from ai.agents.base.analytical_agent import AnalyticalAgent


class RankerAgent(AnalyticalAgent):
    """
    Agent for ranking and aggregation analysis.

    Priorities:
    - Top N rankings
    - Comparative analysis
    - Group aggregations
    - Sorted rankings
    """

    @property
    def name(self) -> str:
        return "ranker"

    @property
    def primary_mart(self) -> str:
        return "aggregates"

    @property
    def analytical_focus(self) -> list[str]:
        return [
            "top_n",
            "rankings",
            "comparisons",
            "aggregations",
        ]

    def build_system_prompt(self) -> str:
        """Build ranking-focused system prompt."""
        return """
You are a ranking and aggregation analytics expert.

Your role:
- Rank entities by performance metrics
- Compare groups and segments
- Aggregate and summarize data
- Identify top performers

Analytical priorities:
- What are the top N performers?
- How do groups compare?
- What are the aggregate metrics?
- What's the ranking order?

SQL style:
- ORDER BY with LIMIT
- GROUP BY for aggregation
- Window functions for ranking
- RANK/ROW_NUMBER for positioning

Generate PostgreSQL SQL that provides clear rankings and comparisons.
""".strip()