from services.sql_execution import create_postgres_engine


def create_base_schemas(database_url: str) -> None:
    engine = create_postgres_engine(database_url)
    ddl = """
    CREATE SCHEMA IF NOT EXISTS bronze;
    CREATE SCHEMA IF NOT EXISTS raw;
    CREATE SCHEMA IF NOT EXISTS silver;
    CREATE SCHEMA IF NOT EXISTS gold;
    CREATE SCHEMA IF NOT EXISTS ops;
    """

    raw_conn = engine.raw_connection()

    try:
        with raw_conn.cursor() as cursor:
            cursor.execute(ddl)
        raw_conn.commit()
    except Exception:
        raw_conn.rollback()
        raise
    finally:
        raw_conn.close()
