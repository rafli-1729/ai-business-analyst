from warehouse.quality.checks import (
    ensure_quality_tables,
    record_validation_result,
)

from warehouse.quality.validations.silver.orders import (
    validate_orders_no_null_ids,
    validate_orders_unique_ids,
)

from warehouse.quality.validations.silver.payments import (
    validate_payment_values_positive,
)

from warehouse.quality.validations.gold.sales_summary import (
    validate_sales_summary_non_negative,
)


VALIDATIONS = [
    validate_orders_no_null_ids,
    validate_orders_unique_ids,
    validate_payment_values_positive,
    validate_sales_summary_non_negative,
]


def run_quality_checks(engine):

    ensure_quality_tables(engine)

    results = []

    for validation in VALIDATIONS:

        result = validation(engine)

        record_validation_result(
            engine=engine,
            validation_name=result["validation_name"],
            layer_name=result["layer_name"],
            passed=result["passed"],
            issue_count=result["issue_count"],
        )

        results.append(result)

    return results