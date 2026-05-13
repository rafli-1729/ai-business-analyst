from dagster import AssetExecutionContext, MaterializeResult, asset


@asset(group_name="gold", compute_kind="sql", deps=["silver_warehouse"])
def gold_analytics_marts(context: AssetExecutionContext) -> MaterializeResult:
    context.log.info("Gold marts are built by the ordered warehouse ELT asset.")
    return MaterializeResult(metadata={"serving_table": "gold.order_item_facts"})
