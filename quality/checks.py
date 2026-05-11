from sqlalchemy import text


def count_quality_issues(engine) -> int:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM silver.data_quality_issues"))
        return int(result.scalar() or 0)


def summarize_quality_issues(engine):
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
