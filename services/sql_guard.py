import re

FORBIDDEN = {
    "drop", "delete", "update", "insert", "alter", "truncate", "create", "grant", "revoke"
}
READ_ONLY_START = re.compile(r"\b(select|with)\b", flags=re.IGNORECASE)
READ_ONLY_LINE_START = re.compile(r"^\s*(?:sql\s*:\s*)?(select|with)\b", flags=re.IGNORECASE | re.MULTILINE)
FENCED_BLOCK = re.compile(r"```(?:sql|postgresql|pgsql)?\s*(.*?)```", flags=re.IGNORECASE | re.DOTALL)


class SqlValidationError(ValueError):
    pass


def strip_comments(sql: str) -> str:
    sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql.strip()


def extract_sql_candidate(raw_sql: str) -> str:
    cleaned = raw_sql.strip()

    fenced_blocks = FENCED_BLOCK.findall(cleaned)
    for block in fenced_blocks:
        if READ_ONLY_START.search(block):
            return _from_first_read_only_keyword(block).strip()

    return _from_first_read_only_keyword(cleaned).strip()


def validate_sql_is_read_only(sql: str) -> str:
    without_comments = strip_comments(sql)
    if not without_comments:
        raise SqlValidationError("Empty SQL")

    if any(re.search(rf"\b{kw}\b", without_comments.lower()) for kw in FORBIDDEN):
        raise SqlValidationError("Dangerous SQL detected")

    cleaned = extract_sql_candidate(without_comments)
    statements = split_sql_statements(cleaned)
    if not statements:
        raise SqlValidationError("Only SELECT/CTE SELECT queries are allowed")

    stmt = statements[0]
    lowered = stmt.lower()

    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise SqlValidationError("Only SELECT/CTE SELECT queries are allowed")

    for extra in statements[1:]:
        if _looks_like_sql_statement(extra):
            raise SqlValidationError("Only single statement is allowed")

    return stmt.rstrip(";").strip()


def split_sql_statements(sql: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    in_single_quote = False
    in_double_quote = False
    index = 0

    while index < len(sql):
        char = sql[index]
        next_char = sql[index + 1] if index + 1 < len(sql) else ""

        if char == "'" and not in_double_quote:
            current.append(char)
            if in_single_quote and next_char == "'":
                current.append(next_char)
                index += 2
                continue
            in_single_quote = not in_single_quote
            index += 1
            continue

        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            current.append(char)
            index += 1
            continue

        if char == ";" and not in_single_quote and not in_double_quote:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            index += 1
            continue

        current.append(char)
        index += 1

    statement = "".join(current).strip()
    if statement:
        statements.append(statement)
    return statements


def _from_first_read_only_keyword(text: str) -> str:
    match = READ_ONLY_LINE_START.search(text)
    if match:
        return text[match.start(1) :]

    match = re.search(r"\bsql\s*:\s*(select|with)\b", text, flags=re.IGNORECASE)
    if match:
        return text[match.start(1) :]

    return text


def _looks_like_sql_statement(text: str) -> bool:
    normalized = text.strip().lower()
    if not normalized:
        return False
    sql_starts = ("select", "with", "explain", "analyze", "show")
    return normalized.startswith(sql_starts)
