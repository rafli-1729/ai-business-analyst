from sqlalchemy import text


def validate_orders_no_null_ids(engine):

    query = text(
        """
        SELECT COUNT(*)
        FROM silver.orders
        WHERE order_id IS NULL
        """
    )

    with engine.connect() as conn:
        issue_count = conn.execute(query).scalar()

    return {
        "validation_name": "orders_no_null_ids",
        "layer_name": "silver",
        "passed": issue_count == 0,
        "issue_count": issue_count,
    }


def validate_orders_unique_ids(engine):

    query = text(
        """
        SELECT COUNT(*)
        FROM (
            SELECT
                order_id
            FROM silver.orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) AS duplicates
        """
    )

    with engine.connect() as conn:
        issue_count = conn.execute(query).scalar()

    return {
        "validation_name": "orders_unique_ids",
        "layer_name": "silver",
        "passed": issue_count == 0,
        "issue_count": issue_count,
    }