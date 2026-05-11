import json
from pathlib import Path
from typing import Any, Dict

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema_metadata.json"

def load_schema_metadata() -> Dict[str, Any]:

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def render_schema_for_prompt(metadata: Dict[str, Any]) -> str:

    sections = []

    # ==================================================
    # DATABASE OVERVIEW
    # ==================================================

    overview = metadata.get("database_overview", {})

    sections.append(
        f"""
        DATABASE OVERVIEW:
        Name: {overview.get('name', 'Unknown')}
        Description: {overview.get('description', '')}
        Business Domain: {overview.get('primary_business_domain', '')}
        """.strip()
    )

    # ==================================================
    # DATABASE LAYERS
    # ==================================================

    layers = metadata.get("database_layers", [])

    if layers:

        layer_lines = [
            """
            ==================================================
            DATABASE LAYERS
            ==================================================
            """.strip()
        ]

        for layer in layers:
            layer_lines.append(
                f"- {layer.get('schema')}: {layer.get('description', '')}"
            )

        sections.append("\n".join(layer_lines))

    # ==================================================
    # TABLES
    # ==================================================

    for table in metadata.get("tables", []):

        table_lines = []

        table_lines.append(
            f"""
            ==================================================
            TABLE: {table.get('name')}
            ==================================================
            """.strip()
        )

        table_lines.append(
            f"Description: {table.get('description', '')}"
        )

        # primary key
        if table.get("primary_key"):

            primary_key = table["primary_key"]

            if isinstance(primary_key, list):
                primary_key = ", ".join(primary_key)

            table_lines.append(
                f"Primary Key: {primary_key}"
            )

        # business rules
        business_rules = table.get("business_rules", [])

        if business_rules:

            table_lines.append("Business Rules:")

            for rule in business_rules:
                table_lines.append(f"- {rule}")

        # columns
        table_lines.append("\nColumns:")

        for column in table.get("columns", []):

            col_name = column.get("name", "")
            col_desc = column.get("description", "")
            semantic_type = column.get("semantic_type", "")

            table_lines.append(
                f"""
                - {col_name}
                Description: {col_desc}
                Semantic Type: {semantic_type}
                """.strip()
            )

        sections.append("\n".join(table_lines))

    # ==================================================
    # ANALYTICS TABLES
    # ==================================================

    semantic_tables = metadata.get("semantic_tables", [])

    for table in semantic_tables:

        table_lines = []

        table_lines.append(
            f"""
            ==================================================
            ANALYTICS TABLE: {table.get('name')}
            ==================================================
            """.strip()
        )

        table_lines.append(
            f"Layer: {table.get('layer', '')}"
        )

        table_lines.append(
            f"Description: {table.get('description', '')}"
        )

        grain = table.get("grain")

        if grain:
            table_lines.append(f"Grain: {grain}")

        preferred_for = table.get("preferred_for", [])

        if preferred_for:
            table_lines.append("Prefer this table for:")

            for use_case in preferred_for:
                table_lines.append(f"- {use_case}")

        table_lines.append("\nColumns:")

        for column in table.get("columns", []):

            table_lines.append(
                f"""
                - {column.get('name', '')}
                Description: {column.get('description', '')}
                Semantic Type: {column.get('semantic_type', '')}
                """.strip()
            )

        sections.append("\n".join(table_lines))

    # ==================================================
    # RELATIONSHIPS
    # ==================================================

    relationships = metadata.get("relationships", [])

    if relationships:

        relationship_lines = [
            """
            ==================================================
            RELATIONSHIPS
            ==================================================
            """.strip()
        ]

        for rel in relationships:

            relationship_lines.append(
                f"- {rel['source']} -> {rel['target']} ({rel['relationship_type']})"
            )

        sections.append("\n".join(relationship_lines))

    # ==================================================
    # GLOBAL BUSINESS RULES
    # ==================================================

    global_rules = metadata.get("global_business_rules", [])

    if global_rules:

        rule_lines = [
            """
            ==================================================
            GLOBAL BUSINESS RULES
            ==================================================
            """.strip()
        ]

        for rule in global_rules:
            rule_lines.append(f"- {rule}")

        sections.append("\n".join(rule_lines))

    return "\n\n".join(sections)
