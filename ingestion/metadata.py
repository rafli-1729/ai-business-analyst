import hashlib
from datetime import datetime, timezone

from sqlalchemy import text


def file_checksum(path) -> str:
    hash_ = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hash_.update(chunk)

    return hash_.hexdigest()


def ensure_ingestion_metadata(engine, ops_schema: str = "ops") -> None:
    ddl = f"""
    CREATE SCHEMA IF NOT EXISTS {ops_schema};

    CREATE TABLE IF NOT EXISTS {ops_schema}.ingestion_runs (
        run_id TEXT PRIMARY KEY,
        source_file TEXT NOT NULL,
        source_checksum TEXT NOT NULL,
        target_schema TEXT NOT NULL,
        target_table TEXT NOT NULL,
        status TEXT NOT NULL,
        processed_chunks INTEGER DEFAULT 0,
        total_rows BIGINT,
        inserted_rows BIGINT,
        started_at TIMESTAMPTZ NOT NULL,
        finished_at TIMESTAMPTZ
    );
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


def has_successful_run(
    engine,
    source_file: str,
    checksum: str,
    target_schema: str,
    target_table: str,
    ops_schema: str = "ops",
) -> bool:
    query = text(
        f"""
        SELECT 1
        FROM {ops_schema}.ingestion_runs
        WHERE source_file = :source_file
          AND source_checksum = :checksum
          AND target_schema = :target_schema
          AND target_table = :target_table
          AND status = 'success'
        LIMIT 1
        """
    )

    with engine.connect() as conn:
        return conn.execute(
            query,
            {
                "source_file": source_file,
                "checksum": checksum,
                "target_schema": target_schema,
                "target_table": target_table,
            },
        ).first() is not None


def record_ingestion_run(
    engine,
    run_id: str,
    source_file: str,
    checksum: str,
    target_schema: str,
    target_table: str,
    status: str,
    total_rows: int = 0,
    processed_chunks: int = 0,
    inserted_rows: int = 0,
    ops_schema: str = "ops",
) -> None:
    now = datetime.now(timezone.utc)

    with engine.begin() as conn:
        conn.execute(
            text(
                f"""
                INSERT INTO {ops_schema}.ingestion_runs (
                    run_id,
                    source_file,
                    source_checksum,
                    target_schema,
                    target_table,
                    status,
                    processed_chunks,
                    total_rows,
                    inserted_rows,
                    started_at,
                    finished_at
                )
                VALUES (
                    :run_id,
                    :source_file,
                    :source_checksum,
                    :target_schema,
                    :target_table,
                    :status,
                    :processed_chunks,
                    :total_rows,
                    :inserted_rows,
                    :started_at,
                    CASE
                        WHEN :status IN ('success', 'failed')
                        THEN :finished_at
                        ELSE NULL
                    END
                )
                ON CONFLICT (run_id)
                DO UPDATE SET
                    status = excluded.status,
                    processed_chunks = excluded.processed_chunks,
                    total_rows = excluded.total_rows,
                    inserted_rows = excluded.inserted_rows,
                    finished_at = excluded.finished_at
                """
            ),
            {
                "run_id": run_id,
                "source_file": source_file,
                "source_checksum": checksum,
                "target_schema": target_schema,
                "target_table": target_table,
                "status": status,
                "processed_chunks": processed_chunks,
                "total_rows": total_rows,
                "inserted_rows": inserted_rows,
                "started_at": now,
                "finished_at": now,
            },
        )
