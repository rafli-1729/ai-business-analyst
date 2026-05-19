import re

def remove_markdown_tables(text: str) -> str:
    """Remove markdown tables from text."""
    # Simple regex to remove lines starting and ending with |
    lines = text.split("\n")
    cleaned_lines = [line for line in lines if not (line.strip().startswith("|") and line.strip().endswith("|"))]
    return "\n".join(cleaned_lines).strip()

def summarize_query_result(question: str, sql: str, rows: list) -> str:
    """Stub for summarization."""
    return f"Summary of results for: {question}"
