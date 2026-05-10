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

            table_lines.append(
                f"Primary Key: {table['primary_key']}"
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
