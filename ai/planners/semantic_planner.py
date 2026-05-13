from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "or",
    "the",
    "to",
    "with",
}


@dataclass(frozen=True)
class CandidateTable:
    name: str
    layer: str
    description: str
    grain: str
    preferred_for: tuple[str, ...]
    columns: tuple[str, ...]
    score: int


@dataclass(frozen=True)
class QueryPlan:
    intent: str
    metric_hints: tuple[str, ...]
    dimension_hints: tuple[str, ...]
    candidate_tables: tuple[CandidateTable, ...]

    def render_for_prompt(self) -> str:
        table_lines = []
        for table in self.candidate_tables:
            preferred = "; ".join(table.preferred_for[:3]) or "general analytics"
            columns = ", ".join(table.columns[:10]) or "see schema context"
            table_lines.append(
                f"- {table.name} ({table.layer}, score={table.score}): "
                f"{table.description} Grain: {table.grain or 'not specified'}. "
                f"Useful for: {preferred}. Relevant columns: {columns}."
            )

        return "\n".join(
            [
                f"Intent: {self.intent}",
                f"Metric hints: {', '.join(self.metric_hints) or 'none'}",
                f"Dimension hints: {', '.join(self.dimension_hints) or 'none'}",
                "Candidate tables:",
                *table_lines,
            ]
        )


def build_query_plan(question: str, schema_metadata: dict[str, Any]) -> QueryPlan:
    semantic_context = schema_metadata.get("semantic_context", "")
    question_tokens = _tokens(question)
    tables = _parse_semantic_tables(semantic_context)
    scored_tables = _score_tables(tables, question_tokens)
    selected_tables = tuple(scored_tables[:4])

    return QueryPlan(
        intent=_infer_intent(question_tokens, selected_tables),
        metric_hints=_select_columns(selected_tables, "metric", question_tokens),
        dimension_hints=_select_columns(
            selected_tables,
            ("categorical", "location", "date", "boolean"),
            question_tokens,
        ),
        candidate_tables=selected_tables,
    )


def _parse_semantic_tables(semantic_context: str) -> list[CandidateTable]:
    tables: list[CandidateTable] = []
    for block in re.split(r"\n### Analytics table:\s+", semantic_context)[1:]:
        name, _, body = block.partition("\n")
        layer = _first_match(body, r"Layer:\s*(.+)") or "unknown"
        grain = _first_match(body, r"Grain:\s*(.+)") or ""
        description = _first_match(body, r"Description:\s*(.+)") or ""
        preferred_for = tuple(_section_items(body, "Preferred for"))
        columns = tuple(_column_names(body))
        tables.append(
            CandidateTable(
                name=name.strip(),
                layer=layer.strip(),
                description=description.strip(),
                grain=grain.strip(),
                preferred_for=preferred_for,
                columns=columns,
                score=0,
            )
        )
    return tables


def _score_tables(tables: list[CandidateTable], question_tokens: set[str]) -> list[CandidateTable]:
    scored: list[CandidateTable] = []
    for table in tables:
        text = " ".join(
            [
                table.name,
                table.description,
                table.grain,
                " ".join(table.preferred_for),
                " ".join(table.columns),
            ]
        )
        table_tokens = _tokens(text)
        score = len(question_tokens & table_tokens)
        if table.name == "gold.order_item_facts":
            score += 1
        if table.layer == "gold":
            score += 1
        scored.append(
            CandidateTable(
                name=table.name,
                layer=table.layer,
                description=table.description,
                grain=table.grain,
                preferred_for=table.preferred_for,
                columns=table.columns,
                score=score,
            )
        )

    return sorted(scored, key=lambda table: table.score, reverse=True)


def _select_columns(
    tables: tuple[CandidateTable, ...],
    semantic_types: str | tuple[str, ...],
    question_tokens: set[str],
) -> tuple[str, ...]:
    requested_types = {semantic_types} if isinstance(semantic_types, str) else set(semantic_types)
    hints: list[str] = []
    for table in tables:
        for column in table.columns:
            name, column_type = _split_column(column)
            column_tokens = _tokens(name)
            if column_type in requested_types and (column_tokens & question_tokens or len(hints) < 3):
                hints.append(name)

    return tuple(dict.fromkeys(hints[:6]))


def _infer_intent(question_tokens: set[str], tables: tuple[CandidateTable, ...]) -> str:
    table_text = " ".join(table.name for table in tables)
    if "monthly" in table_text or {"trend", "growth", "month", "monthly"} & question_tokens:
        return "trend"
    if {"top", "highest", "best", "rank", "ranking"} & question_tokens:
        return "ranking"
    if {"why", "reason", "explain", "driver", "drivers"} & question_tokens:
        return "diagnostic"
    if {"quality", "validation", "audit", "clean"} & question_tokens:
        return "data_quality"
    return "general_analytics"


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower().replace("_", " "))
        if len(token) > 1 and token not in STOPWORDS
    }


def _first_match(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def _section_items(text: str, heading: str) -> list[str]:
    match = re.search(rf"{re.escape(heading)}:\n(?P<body>(?:- .+\n?)+)", text)
    if not match:
        return []
    return [line[2:].strip() for line in match.group("body").splitlines() if line.startswith("- ")]


def _column_names(text: str) -> list[str]:
    columns_section = re.search(r"Columns:\n(?P<body>(?:- .+\n?)+)", text)
    if not columns_section:
        return []
    return [line[2:].strip() for line in columns_section.group("body").splitlines() if line.startswith("- ")]


def _split_column(column: str) -> tuple[str, str]:
    match = re.match(r"(?P<name>[^\s(]+)\s+\((?P<type>[^)]+)\)", column)
    if not match:
        return column, ""
    return match.group("name"), match.group("type")
