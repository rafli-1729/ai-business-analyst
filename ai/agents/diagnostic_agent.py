"""
DiagnosticAgent for root cause and driver analysis.

Specializes in:
- Identifying root causes
- Finding performance drivers
- Multi-step diagnostic reasoning
"""

from ai.agents.base.analytical_agent import AnalyticalAgent


class DiagnosticAgent(AnalyticalAgent):
    """
    Agent for diagnostic and root cause analysis.

    Priorities:
    - Root cause identification
    - Driver discovery
    - Supporting evidence
    - Causal reasoning
    """

    @property
    def name(self) -> str:
        return "diagnostic"

    @property
    def primary_mart(self) -> str:
        return "analytical"

    @property
    def analytical_focus(self) -> list[str]:
        return [
            "root_causes",
            "drivers",
            "supporting_evidence",
            "causal_relationships",
        ]

    def build_system_prompt(self) -> str:
        """Build diagnostic-focused system prompt."""
        return """
You are a diagnostic analytics expert specializing in root cause analysis.

Your role:
- Identify performance drivers
- Find root causes of variations
- Provide supporting evidence
- Explain causal relationships

Analytical priorities:
- What changed and why?
- What factors drive this metric?
- What are the root causes?
- What evidence supports this conclusion?

SQL style:
- Multi-step decomposition
- Temporal comparisons
- Driver segmentation
- Supporting detail queries

Generate clear, explainable PostgreSQL SQL that surfaces drivers and causes.
""".strip()