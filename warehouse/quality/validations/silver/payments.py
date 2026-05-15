from sqlalchemy import text


def validate_payment_values_positive(engine):

    query = text(
        """
        SELECT COUNT(*)
        FROM silver.order_payments
        WHERE payment_value < 0
        """
    )

    with engine.connect() as conn:
        issue_count = conn.execute(query).scalar()

    return {
        "validation_name": "payment_values_positive",
        "layer_name": "silver",
        "passed": issue_count == 0,
        "issue_count": issue_count,
    }