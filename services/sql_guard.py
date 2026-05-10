import re

FORBIDDEN = {
    "drop", "delete", "update", "insert", "alter", "truncate", "create", "grant", "revoke"
}


class SqlValidationError(ValueError):
    pass


def strip_comments(sql: str) -> str:
    sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql.strip()


def validate_sql_is_read_only(sql: str) -> str:
    cleaned = strip_comments(sql)
    if not cleaned:
        raise SqlValidationError("Empty SQL")

    statements = [s.strip() for s in cleaned.split(";") if s.strip()]
    if len(statements) != 1:
        raise SqlValidationError("Only single statement is allowed")

    stmt = statements[0]
    lowered = stmt.lower()

    if any(re.search(rf"\b{kw}\b", lowered) for kw in FORBIDDEN):
        raise SqlValidationError("Dangerous SQL detected")

    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise SqlValidationError("Only SELECT/CTE SELECT queries are allowed")

    return stmt
