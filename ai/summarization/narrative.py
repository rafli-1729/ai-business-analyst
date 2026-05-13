import json
import re
import hashlib
from pathlib import Path
from typing import Any


PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "summarization.txt"
SUMMARY_FORMAT_VERSION = "summary-v2-no-markdown-tables"


def summary_prompt_fingerprint() -> str:
    prompt_hash = hashlib.sha256(PROMPT_PATH.read_bytes()).hexdigest()[:12]
    return f"{SUMMARY_FORMAT_VERSION}:{prompt_hash}"


def summarize_query_result(
    llm,
    question: str,
    sql: str,
    rows: list[dict[str, Any]],
    max_tokens: int | None = None,
) -> str:
    if not rows:
        return "No rows were returned for this question."

    preview = rows[:12]
    instructions = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = f"""
            {instructions}

            User question:
            {question}

            Generated SQL:
            {sql}

            Result preview as JSON:
            {json.dumps(preview, ensure_ascii=False, default=str)}

            Write only the summary text.
    """.strip()

    summary = llm.invoke(prompt, request_id="summary", max_tokens=max_tokens)
    return remove_markdown_tables(summary)


def remove_markdown_tables(content: str) -> str:
    lines = content.splitlines()
    cleaned_lines: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        next_line = lines[index + 1] if index + 1 < len(lines) else ""
        if _looks_like_table_row(line) and _looks_like_table_separator(next_line):
            index += 2
            while index < len(lines) and _looks_like_table_row(lines[index]):
                index += 1
            continue
        cleaned_lines.append(line)
        index += 1

    cleaned = "\n".join(cleaned_lines).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned or "Summary unavailable without a table-formatted response."


def _looks_like_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.count("|") >= 2


def _looks_like_table_separator(line: str) -> bool:
    return bool(re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$", line.strip()))
