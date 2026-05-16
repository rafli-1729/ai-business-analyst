"""
Base analytical agent for specialized reasoning.

Provides abstract agent class for domain-specific analytical tasks.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class AnalyticalAgent(ABC):
    """
    Abstract base class for analytical agents.

    Agents are specialized analytical reasoning units that:
    - Generate PostgreSQL SQL with domain-specific prompting
    - Have specific analytical priorities
    - Work with designated marts
    - Employ specialized reasoning strategies
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name identifier."""
        pass

    @property
    @abstractmethod
    def primary_mart(self) -> str:
        """Primary data mart for this agent."""
        pass

    @property
    @abstractmethod
    def analytical_focus(self) -> list[str]:
        """Areas of analytical focus."""
        pass

    @abstractmethod
    def build_system_prompt(self) -> str:
        """
        Build system prompt for SQL generation.

        Returns:
            System prompt string with agent-specific instructions
        """
        pass

    def build_analytical_context(
        self,
        question: str,
        mart: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build analytical context for this agent.

        Args:
            question: User question
            mart: Optional mart override

        Returns:
            Analytical context dictionary
        """
        return {
            "intent": self.analytical_intent,
            "agent": self.name,
            "mart": mart or self.primary_mart,
            "focus": self.analytical_focus,
            "focus_areas": self.analytical_focus,
        }

    @property
    def analytical_intent(self) -> str:
        """
        Get analytical intent type for this agent.

        Returns:
            Intent classification
        """
        return self.name.lower()
