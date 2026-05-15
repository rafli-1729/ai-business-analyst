from sqlalchemy import text

from infra.database.introspection import (
    table_exists,
)


def count_quality_issues(engine) -> int:

    if not table_exists(
        engine,
        "silver",
        "data_quality_issues",
    ):
        return 0

    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM silver.data_quality_issues
                """
            )
        )

        return int(result.scalar() or 0)


def summarize_quality_issues(engine):

    if not table_exists(
        engine,
        "silver",
        "data_quality_issues",
    ):
        return []

    with engine.connect() as conn:
        return conn.execute(
            text(
                """
                SELECT
                    q.table_name,
                    q.issue_type,
                    q.severity,
                    COUNT(*) AS issue_count
                FROM silver.data_quality_issues AS q
                GROUP BY
                    q.table_name,
                    q.issue_type,
                    q.severity
                ORDER BY
                    issue_count DESC,
                    q.table_name,
                    q.issue_type
                """
            )
        ).fetchall()


def ensure_quality_tables(
    engine,
    ops_schema: str = "ops",
) -> None:

    ddl = f"""
    CREATE TABLE IF NOT EXISTS {ops_schema}.data_quality_results (
        validation_name TEXT,
        layer_name TEXT,
        passed BOOLEAN,
        issue_count BIGINT,
        validation_time TIMESTAMPTZ DEFAULT NOW()
    );
    """

    with engine.begin() as conn:
        conn.execute(text(ddl))


def record_validation_result(
    engine,
    validation_name: str,
    layer_name: str,
    passed: bool,
    issue_count: int,
    ops_schema: str = "ops",
):

    query = text(
        f"""
        INSERT INTO {ops_schema}.data_quality_results (
            validation_name,
            layer_name,
            passed,
            issue_count
        )
        VALUES (
            :validation_name,
            :layer_name,
            :passed,
            :issue_count
        )
        """
    )

    with engine.begin() as conn:
        conn.execute(
            query,
            {
                "validation_name": validation_name,
                "layer_name": layer_name,
                "passed": passed,
                "issue_count": issue_count,
            },
        )