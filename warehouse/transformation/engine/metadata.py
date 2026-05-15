from datetime import datetime, timezone

from sqlalchemy import text


def ensure_elt_metadata(
    engine,
    ops_schema: str = "ops",
) -> None:

    ddl = f"""
    CREATE TABLE IF NOT EXISTS {ops_schema}.elt_runs (
        run_id TEXT,
        layer_name TEXT,
        model_name TEXT,
        status TEXT,
        started_at TIMESTAMPTZ,
        finished_at TIMESTAMPTZ,
        execution_seconds FLOAT
    );
    """

    with engine.begin() as conn:
        conn.execute(text(ddl))


def record_elt_run(
    engine,
    run_id: str,
    layer_name: str,
    model_name: str,
    status: str,
    started_at,
    finished_at,
    ops_schema: str = "ops",
) -> None:

    execution_seconds = (
        finished_at - started_at
    ).total_seconds()

    with engine.begin() as conn:
        conn.execute(
            text(
                f"""
                INSERT INTO {ops_schema}.elt_runs (
                    run_id,
                    layer_name,
                    model_name,
                    status,
                    started_at,
                    finished_at,
                    execution_seconds
                )
                VALUES (
                    :run_id,
                    :layer_name,
                    :model_name,
                    :status,
                    :started_at,
                    :finished_at,
                    :execution_seconds
                )
                """
            ),
            {
                "run_id": run_id,
                "layer_name": layer_name,
                "model_name": model_name,
                "status": status,
                "started_at": started_at,
                "finished_at": finished_at,
                "execution_seconds": execution_seconds,
            },
        )