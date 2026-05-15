import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent.parent
SEMANTIC_CONTEXT_PATH = ROOT / "warehouse" / "semantic" / "semantic_context.md"
TABLE_RELATIONS_PATH = ROOT / "warehouse" / "semantic" / "table_relations.json"

def load_schema_metadata() -> Dict[str, Any]:
    semantic_context = SEMANTIC_CONTEXT_PATH.read_text(encoding="utf-8")

    with TABLE_RELATIONS_PATH.open("r", encoding="utf-8") as file:
        relations = json.load(file)

    return {
        "schema_version": relations.get("schema_version", "v1"),
        "semantic_context": semantic_context,
        "relations": relations,
    }


def load_table_relations() -> Dict[str, Any]:
    with TABLE_RELATIONS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def render_schema_for_prompt(metadata: Dict[str, Any], question: str | None = None) -> str:
    semantic_context = metadata.get("semantic_context")
    if semantic_context:
        return _select_relevant_semantic_context(semantic_context, question)

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


def _select_relevant_semantic_context(semantic_context: str, question: str | None) -> str:
    if not question:
        return semantic_context

    normalized_question = question.lower()
    always_include = [
        "# ",
        "Schema version:",
        "Business domain:",
        "## Main use cases",
        "## Warehouse layers",
        "## Recommended analytics tables",
    ]
    topic_keywords = {
        "gold.order_item_facts": ["default", "revenue", "sales", "delivery", "customer", "seller", "product", "payment", "review"],
        "gold.monthly_revenue": ["month", "monthly", "trend", "growth", "over time"],
        "gold.category_performance": ["category", "product category", "top product", "revenue"],
        "gold.state_performance": ["state", "geography", "location"],
        "gold.seller_performance": ["seller"],
        "gold.payment_method_performance": ["payment", "installment"],
        "gold.delivery_performance": ["delivery", "late", "shipping"],
        "silver.": ["quality", "clean", "validation", "audit"],
        "raw": ["raw", "source", "ingestion"],
        "bronze": ["raw", "source", "ingestion"],
    }

    blocks = semantic_context.split("\n### ")
    header = blocks[0]
    selected_blocks = [header]

    for block in blocks[1:]:
        block_text = "### " + block
        lowered_block = block_text.lower()
        include = any(marker.lower() in lowered_block for marker in always_include)

        for marker, keywords in topic_keywords.items():
            if marker.lower() in lowered_block and any(keyword in normalized_question for keyword in keywords):
                include = True
                break

        if include:
            selected_blocks.append(block_text)

    compact_context = "\n\n".join(selected_blocks)
    return compact_context if len(compact_context) < len(semantic_context) else semantic_context
