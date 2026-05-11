from psycopg2 import sql


def quote_ident(name: str) -> sql.Identifier:
    return sql.Identifier(name)


def quoted_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def quoted_table(schema_name: str, table_name: str) -> str:
    return f"{quoted_identifier(schema_name)}.{quoted_identifier(table_name)}"


def quoted_columns(columns: list[str]) -> str:
    return ", ".join(quoted_identifier(column) for column in columns)


def normalize_columns(value) -> list[str]:
    if isinstance(value, str):
        return [value]

    if isinstance(value, list):
        return value

    return []
