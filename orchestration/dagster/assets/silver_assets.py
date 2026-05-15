import os

from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, asset

from orchestration.pipelines.transformation_pipeline import run_warehouse_elt


@asset(group_name="silver", compute_kind="sql", deps=["bronze_olist_sources"])
def silver_warehouse(context: AssetExecutionContext) -> MaterializeResult:
    database_url = os.getenv("INGESTER_DB_URL", "").strip()
    if not database_url:
        raise ValueError("Missing INGESTER_DB_URL")

    result = run_warehouse_elt(database_url)
    context.log.info("Warehouse ELT run %s completed", result["run_id"])

    return MaterializeResult(
        metadata={
            "elt_run_id": result["run_id"],
            "executed_files": MetadataValue.json(result["executed_files"]),
            "quality_issue_count": result.get("quality_issue_count", 0),
        }
    )
