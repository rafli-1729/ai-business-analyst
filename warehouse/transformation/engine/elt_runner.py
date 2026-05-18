import uuid
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from sqlalchemy import text

from infra.database.engine import create_postgres_engine, execute_sql_file
from warehouse.quality.checks import count_quality_issues
from infra.observability.logger import setup_logging

logger = setup_logging()

@dataclass(frozen=True)
class EltConfig:
    database_url: str
    sql_root: Path = Path("warehouse/transformation/models")
    layer_order: tuple[str, ...] = ("reference", "bronze", "master", "silver", "gold")
    ops_schema: str = "ops"


def run_warehouse_elt(database_url: str):
    """Wrapper to maintain compatibility with existing pipeline architecture."""
    config = EltConfig(database_url=database_url)
    return run_elt(config)


def _sql_files_for_layers(config: EltConfig) -> list[Path]:
    files: list[Path] = []

    for layer_name in config.layer_order:
        layer_dir = config.sql_root / layer_name
        if layer_dir.exists():
            files.extend(sorted(layer_dir.glob("*.sql")))

    return files


def _ensure_elt_run_table(engine, ops_schema: str) -> None:
    ddl = f"""
    SET default_transaction_read_only = off;
    CREATE SCHEMA IF NOT EXISTS {ops_schema};

    CREATE TABLE IF NOT EXISTS {ops_schema}.elt_runs (
        run_id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        executed_files TEXT[] NOT NULL DEFAULT '{{}}',
        quality_issue_count BIGINT,
        started_at TIMESTAMPTZ NOT NULL,
        finished_at TIMESTAMPTZ
    );
    """

    with engine.connect() as conn:
        conn.execute(text(ddl))


def _record_elt_run(
    engine,
    ops_schema: str,
    run_id: str,
    status: str,
    executed_files: Iterable[str],
    started_at: datetime,
    quality_issue_count: int | None = None,
) -> None:
    finished_at = datetime.now(timezone.utc) if status in {"success", "failed"} else None

    with engine.connect() as conn:
        conn.execute(
            text(
                f"""
                INSERT INTO {ops_schema}.elt_runs (
                    run_id,
                    status,
                    executed_files,
                    quality_issue_count,
                    started_at,
                    finished_at
                )
                VALUES (
                    :run_id,
                    :status,
                    :executed_files,
                    :quality_issue_count,
                    :started_at,
                    :finished_at
                )
                ON CONFLICT (run_id)
                DO UPDATE SET
                    status = excluded.status,
                    executed_files = excluded.executed_files,
                    quality_issue_count = excluded.quality_issue_count,
                    finished_at = excluded.finished_at
                """
            ),
            {
                "run_id": run_id,
                "status": status,
                "executed_files": list(executed_files),
                "quality_issue_count": quality_issue_count,
                "started_at": started_at,
                "finished_at": finished_at,
            },
        )


def run_elt(config: EltConfig) -> dict:
    sql_files = _sql_files_for_layers(config)

    if not sql_files:
        raise FileNotFoundError(f"No SQL files found under {config.sql_root}")

    engine = create_postgres_engine(config.database_url)
    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)
    executed_files: list[str] = []

    _ensure_elt_run_table(engine, config.ops_schema)
    _record_elt_run(
        engine,
        config.ops_schema,
        run_id,
        "running",
        executed_files,
        started_at
    )

    try:
        for path in sql_files:
            relative_path = str(path.relative_to(config.sql_root)).replace("\\", "/")
            logger.info(f"Executing ELT SQL: {relative_path}")
            execute_sql_file(engine, path)
            executed_files.append(relative_path)
            _record_elt_run(
                engine,
                config.ops_schema,
                run_id,
                "running",
                executed_files,
                started_at
            )

        quality_issue_count = count_quality_issues(engine)
        _record_elt_run(
            engine,
            config.ops_schema,
            run_id,
            "success",
            executed_files,
            started_at,
            quality_issue_count=quality_issue_count,
        )

        return {
            "run_id": run_id,
            "status": "success",
            "executed_files": executed_files,
            "quality_issue_count": quality_issue_count,
        }

    except Exception:
        _record_elt_run(
            engine,
            config.ops_schema,
            run_id,
            "failed",
            executed_files,
            started_at
        )
        raise
