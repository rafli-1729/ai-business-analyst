"""
PromptComposer for building modular prompts.

Extracts prompt building logic from QueryService.
Supports context-aware prompt composition.
"""

from typing import Optional, Dict, Any
from ai.providers.schema_context_provider import SchemaContextProvider


class PromptComposer:
    """
    Composes SQL generation prompts with context.

    Manages:
    - Base prompt templates
    - Context injection
    - Schema inclusion
    - Agent-specific prompting
    """

    def __init__(self, schema_provider: SchemaContextProvider):
        """
        Initialize prompt composer.

        Args:
            schema_provider: Schema context provider
        """
        self.schema_provider = schema_provider

    def build_sql_generation_prompt(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        agent_instructions: str = "",
    ) -> str:
        """
        Build SQL generation prompt.

        Args:
            question: User question
            context: Optional analytical context
            agent_instructions: Optional agent-specific instructions

        Returns:
            Composed prompt string
        """
        context_text = ""
        if context:
            context_text = f"""
Analytical Context:
{self._format_context(context)}
"""

        agent_text = ""
        if agent_instructions:
            agent_text = f"""
Agent Instructions:
{agent_instructions}
"""

        schema_text = self.schema_provider.render_for_prompt(question)

        return f"""
You are a PostgreSQL analytics expert.

Convert the user question into PostgreSQL SQL.

Return ONLY PostgreSQL query.

Rules:
- Use PostgreSQL syntax.
- Use read-only SQL only.
- Prefer gold tables for business analytics.
- Use silver tables for audits and validations.
- Avoid bronze/raw unless explicitly requested.
- Prefer simple and explainable SQL.
- Do not return markdown.
- Do not explain the query.
- If you don't find any aggregations tables for the context,
  use the most relevant tables from the schema and aggregate it.

{context_text}{agent_text}

Schema:
{schema_text}

Question:
{question}
""".strip()

    def build_sql_repair_prompt(
        self,
        question: str,
        original_sql: str,
        validation_error: str,
    ) -> str:
        """
        Build SQL repair prompt for failed queries.

        Args:
            question: Original question
            original_sql: Failed SQL
            validation_error: Error message

        Returns:
            Repair prompt string
        """
        schema_text = self.schema_provider.render_for_prompt(question)

        return f"""
The previous SQL response was rejected by the validator.

Return exactly one PostgreSQL read-only query.

Rules:
- Use only SELECT or WITH.
- No markdown.
- No explanations.
- No comments.
- No multiple statements.

Validation error:
{validation_error}

Previous response:
{original_sql}

Original question:
{question}

Schema:
{schema_text}
""".strip()

    @staticmethod
    def _format_context(context: Dict[str, Any]) -> str:
        """Format context for inclusion in prompt."""
        lines = []
        for key, value in context.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
