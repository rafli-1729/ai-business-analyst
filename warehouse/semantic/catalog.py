import json
from pathlib import Path
from typing import Any


DEFAULT_SEMANTIC_CONTEXT_PATH = Path(__file__).resolve().parent / "semantic_context.md"
DEFAULT_TABLE_RELATIONS_PATH = Path(__file__).resolve().parent / "table_relations.json"


class SemanticCatalog:
    def __init__(
        self,
        semantic_context_path: Path = DEFAULT_SEMANTIC_CONTEXT_PATH,
        table_relations_path: Path = DEFAULT_TABLE_RELATIONS_PATH,
    ):
        self.semantic_context_path = semantic_context_path
        self.table_relations_path = table_relations_path
        self.semantic_context = self.semantic_context_path.read_text(encoding="utf-8")
        self.relations = self._load_relations()

    def _load_relations(self) -> dict[str, Any]:
        with self.table_relations_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def schema_version(self) -> str:
        return self.relations.get("schema_version", "v1")

    def analytics_tables(self) -> list[dict[str, Any]]:
        return [
            table
            for table in self.relations.get("tables", [])
            if (table.get("layer") == "gold" or str(table.get("name", "")).startswith("gold."))
        ]

    def relationships(self) -> list[dict[str, Any]]:
        return self.relations.get("relationships", [])
