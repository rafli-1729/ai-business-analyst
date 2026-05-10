import json
from pathlib import Path
from typing import Any, Dict

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema_metadata.json"


def load_schema_metadata() -> Dict[str, Any]:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def render_schema_for_prompt(metadata: Dict[str, Any]) -> str:
    sections = [f"SCHEMA_VERSION: {metadata.get('schema_version', 'unknown')}"]
    for table in metadata.get("tables", []):
        cols = ", ".join(table.get("columns", []))
        sections.append(f"Table {table['name']}: {table.get('description', '')}\nColumns: {cols}")
    rels = metadata.get("relationships", [])
    if rels:
        sections.append("Relationships:\n- " + "\n- ".join(rels))
    return "\n\n".join(sections)
