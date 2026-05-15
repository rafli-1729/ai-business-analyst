from sqlalchemy import text


def validate_sales_summary_non_negative(engine):

    query = text(
        """
        SELECT COUNT(*)
        FROM gold.sales_summary
        WHERE revenue < 0
        """
    )

    with engine.connect() as conn:
        issue_count = conn.execute(query).scalar()

    return {
        "validation_name": "sales_summary_non_negative",
        "layer_name": "gold",
        "passed": issue_count == 0,
        "issue_count": issue_count,
    }