from pathlib import Path

from psycopg2 import sql
from sqlalchemy import create_engine, text


def create_postgres_engine(database_url: str):
    connect_args = {
        "sslmode": "require",
        "options": "-c statement_timeout=300000 -c default_transaction_read_only=on"  # 5 minutes in milliseconds
    }
    
    # Supabase pooler optimization
    if "pooler.supabase.com" in database_url or ":6543" in database_url:
        pass

    return create_engine(
        database_url, 
        connect_args=connect_args,
        # Required for massive ingestion speed and DDL compatibility
        isolation_level="AUTOCOMMIT"
    )


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
    if not sql_text.strip():
        return

    with engine.connect() as conn:
        conn.execute(text(sql_text))


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
