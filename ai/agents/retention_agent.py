"""
RetentionAgent for customer retention and churn analysis.

Specializes in:
- Repeat customer analysis
- Churn identification
- Purchase cadence
- Cohort retention
"""

from ai.agents.base.analytical_agent import AnalyticalAgent


class RetentionAgent(AnalyticalAgent):
    """
    Agent for retention and churn analysis.

    Priorities:
    - Repeat customers
    - Churn identification
    - Purchase cadence
    - Cohort retention logic
    """

    @property
    def name(self) -> str:
        return "retention"

    @property
    def primary_mart(self) -> str:
        return "retention"

    @property
    def analytical_focus(self) -> list[str]:
        return [
            "repeat_customers",
            "churn",
            "purchase_cadence",
            "cohort_retention",
            "retention_rates",
        ]

    def build_system_prompt(self) -> str:
        """Build retention-focused system prompt."""
        return """
You are a retention and churn analytics expert.

Your role:
- Identify repeat vs one-time customers
- Measure and predict churn
- Analyze purchase cadence
- Cohort-based retention tracking
- Lifecycle stage analysis

Analytical priorities:
- What's our repeat customer rate?
- How many customers are churning?
- What's the purchase cadence?
- Which cohorts retain best?
- What drives retention?

SQL style:
- Repeat purchase identification
- Churn cohort analysis
- Time between purchases
- Retention rate calculations
- Lifecycle stage bucketing

Generate PostgreSQL SQL that reveals retention patterns and churn risk.
""".strip()
