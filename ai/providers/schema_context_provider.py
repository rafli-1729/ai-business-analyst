"""
SchemaContextProvider for managing analytical schema context.

Extracts schema management responsibilities from QueryService.
Provides schema metadata and rendering for prompts.
"""

from typing import Any, Dict
from ai.services.schema_loader import (
    load_schema_metadata,
    render_schema_for_prompt,
)


class SchemaContextProvider:
    """
    Provides schema context for analytical queries.

    Manages:
    - Schema metadata loading
    - Schema versioning
    - Prompt-ready schema rendering
    """

    def __init__(self):
        """Initialize schema context."""
        self.metadata = load_schema_metadata()
        self.version = self.metadata.get("schema_version", "v1")

    def get_metadata(self) -> Dict[str, Any]:
        """Get full schema metadata."""
        return self.metadata

    def get_version(self) -> str:
        """Get schema version."""
        return self.version

    def render_for_prompt(
        self,
        question: str | None = None,
    ) -> str:
        """
        Render schema in prompt-friendly format.

        Args:
            question: Optional question for schema filtering

        Returns:
            Prompt-ready schema string
        """
        return render_schema_for_prompt(self.metadata, question)
