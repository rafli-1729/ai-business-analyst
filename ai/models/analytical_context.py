"""
AnalyticalContext model for enriching query execution.

Provides typed context about the analytical intent,
agent selection, and execution preferences.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AnalyticalContext:
    """
    Analytical context for query execution.

    Attributes:
        intent: Classification of query intent (e.g., 'diagnostic', 'ranking', 'trend')
        agent: Assigned agent name for specialized reasoning
        mart: Primary data mart for the query
        question: Original user question
        refresh: Whether to bypass caching
        row_limit: Maximum rows to return
        focus_areas: Priority areas for the agent
        metadata: Additional context metadata
    """

    intent: str
    agent: str
    mart: str
    question: str
    refresh: bool = False
    row_limit: Optional[int] = None
    focus_areas: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert context to dictionary."""
        return {
            "intent": self.intent,
            "agent": self.agent,
            "mart": self.mart,
            "question": self.question,
            "refresh": self.refresh,
            "row_limit": self.row_limit,
            "focus_areas": self.focus_areas,
            "metadata": self.metadata,
        }
