from pathlib import Path

from psycopg2 import sql
from sqlalchemy import create_engine, text


def create_postgres_engine(database_url: str):
    return create_engine(database_url, connect_args={"sslmode": "require"})


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


def execute_sql_text(engine, sql_text: str) -> None:
    raw_conn = engine.raw_connection()

    try:
        with raw_conn.cursor() as cursor:
            cursor.execute(sql_text)
        raw_conn.commit()
    except Exception:
        raw_conn.rollback()
        raise
    finally:
        raw_conn.close()


def execute_sql_file(engine, path: Path) -> None:
    execute_sql_text(engine, path.read_text(encoding="utf-8"))


def table_exists(engine, schema_name: str, table_name: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = :schema_name
                      AND table_name = :table_name
                )
                """
            ),
            {"schema_name": schema_name, "table_name": table_name},
        )
        return bool(result.scalar())
