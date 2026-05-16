"""
Agent registry for managing specialized analytical agents.

Provides pattern-based agent selection and registration.
Avoids giant if/else branching through registry pattern.
"""

from typing import Dict, Type, Optional
from ai.agents.base.analytical_agent import AnalyticalAgent


class AgentRegistry:
    """
    Registry for analytical agents.

    Manages:
    - Agent registration
    - Agent selection by intent
    - Agent lifecycle
    """

    def __init__(self):
        """Initialize agent registry."""
        self._agents: Dict[str, Type[AnalyticalAgent]] = {}
        self._instances: Dict[str, AnalyticalAgent] = {}

    def register(
        self,
        agent_class: Type[AnalyticalAgent],
        override: bool = False,
    ) -> None:
        """
        Register an agent class.

        Args:
            agent_class: Agent class to register
            override: Allow overriding existing registration

        Raises:
            ValueError: If agent already registered and override=False
        """
        # Get agent name from class
        temp_instance = agent_class()
        agent_name = temp_instance.name.lower()

        if agent_name in self._agents and not override:
            raise ValueError(
                f"Agent '{agent_name}' already registered. "
                f"Use override=True to replace."
            )

        self._agents[agent_name] = agent_class
        # Clear instance cache
        if agent_name in self._instances:
            del self._instances[agent_name]

    def get_agent(self, intent: str) -> Optional[AnalyticalAgent]:
        """
        Get agent instance for intent.

        Args:
            intent: Analytical intent

        Returns:
            Agent instance or None if not found
        """
        intent_key = intent.lower()

        # Return cached instance
        if intent_key in self._instances:
            return self._instances[intent_key]

        # Create new instance
        if intent_key in self._agents:
            agent = self._agents[intent_key]()
            self._instances[intent_key] = agent
            return agent

        return None

    def get_all_agents(self) -> list[AnalyticalAgent]:
        """
        Get all registered agents.

        Returns:
            List of agent instances
        """
        agents = []
        for agent_name in self._agents:
            if agent_name not in self._instances:
                self._instances[agent_name] = self._agents[agent_name]()
            agents.append(self._instances[agent_name])

        return agents

    def has_agent(self, intent: str) -> bool:
        """
        Check if agent exists for intent.

        Args:
            intent: Analytical intent

        Returns:
            True if agent registered
        """
        return intent.lower() in self._agents


# Global registry instance
_registry = AgentRegistry()


def register_agent(
    agent_class: Type[AnalyticalAgent],
    override: bool = False,
) -> None:
    """
    Register agent globally.

    Args:
        agent_class: Agent class to register
        override: Allow overriding existing registration
    """
    _registry.register(agent_class, override=override)


def get_agent(intent: str) -> Optional[AnalyticalAgent]:
    """
    Get agent for intent from global registry.

    Args:
        intent: Analytical intent

    Returns:
        Agent instance or None
    """
    return _registry.get_agent(intent)


def get_all_agents() -> list[AnalyticalAgent]:
    """Get all registered agents."""
    return _registry.get_all_agents()


def get_registry() -> AgentRegistry:
    """Get the global registry instance."""
    return _registry
