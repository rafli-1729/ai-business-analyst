from sqlalchemy import text


def table_exists(
    engine,
    schema_name: str,
    table_name: str,
) -> bool:

    query = text(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = :schema_name
              AND table_name = :table_name
        )
        """
    )

    with engine.connect() as conn:
        return bool(
            conn.execute(
                query,
                {
                    "schema_name": schema_name,
                    "table_name": table_name,
                },
            ).scalar()
        )