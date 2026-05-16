"""
QueryPlan model for execution planning.

Provides typed structure for decomposed query tasks
and execution strategies.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QueryTask:
    """
    Individual task in a query plan.

    Attributes:
        question: Task-specific question
        agent: Agent to handle this task
        mart: Data mart for the task
        intent: Task intent
        order: Execution order
    """

    question: str
    agent: str
    mart: str
    intent: str
    order: int = 0

    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            "question": self.question,
            "agent": self.agent,
            "mart": self.mart,
            "intent": self.intent,
            "order": self.order,
        }


@dataclass
class QueryPlan:
    """
    Execution plan for a query.

    Attributes:
        intent: Overall query intent
        requires_reasoning: Whether multi-step reasoning is needed
        tasks: List of tasks to execute
        agent: Primary agent
        mart: Primary mart
    """

    intent: str
    requires_reasoning: bool
    agent: str
    mart: str
    tasks: list[QueryTask] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert plan to dictionary."""
        return {
            "intent": self.intent,
            "requires_reasoning": self.requires_reasoning,
            "agent": self.agent,
            "mart": self.mart,
            "tasks": [task.to_dict() for task in self.tasks],
        }
