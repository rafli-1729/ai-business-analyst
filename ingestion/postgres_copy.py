import io

import pandas as pd
from psycopg2 import sql


def copy_chunk_to_postgres(
    df: pd.DataFrame,
    schema_name: str,
    table_name: str,
    engine,
) -> None:
    """
    High-performance PostgreSQL COPY ingestion.

    Uses:
    DataFrame -> in-memory CSV buffer -> COPY FROM STDIN

    This is the primary ingestion strategy for bronze loading.
    """

    if df.empty:
        return

    raw_conn = engine.raw_connection()

    try:
        with raw_conn.cursor() as cursor:

            buffer = io.StringIO()

            df.to_csv(
                buffer,
                index=False,
                header=True,
                na_rep="",
            )

            buffer.seek(0)

            copy_stmt = sql.SQL(
                """
                COPY {} ({})
                FROM STDIN
                WITH (
                    FORMAT CSV,
                    HEADER TRUE
                )
                """
            ).format(
                sql.Identifier(schema_name, table_name),
                sql.SQL(", ").join(
                    sql.Identifier(column)
                    for column in df.columns
                ),
            )

            cursor.copy_expert(
                copy_stmt.as_string(cursor),
                buffer,
            )

        raw_conn.commit()

    except Exception:
        raw_conn.rollback()
        raise

    finally:
        raw_conn.close()