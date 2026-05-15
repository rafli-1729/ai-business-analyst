import os

from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, asset

from warehouse.ingestion.config import IngestionConfig
from orchestration.pipelines.ingestion_pipeline import run_ingestion_pipeline


@asset(group_name="bronze", compute_kind="python")
def bronze_olist_sources(context: AssetExecutionContext) -> MaterializeResult:
    database_url = os.getenv("INGESTER_DB_URL", "").strip()
    if not database_url:
        raise ValueError("Missing INGESTER_DB_URL")

    results = run_ingestion_pipeline(
        IngestionConfig(
            database_url=database_url,
        )
    )

    loaded_tables = [
        f"{result.target_schema}.{result.target_table}"
        for result in results
        if result.status in {"success", "skipped"}
    ]

    context.log.info("Bronze ingestion completed for %s tables", len(loaded_tables))

    return MaterializeResult(
        metadata={
            "loaded_table_count": len(loaded_tables),
            "loaded_tables": MetadataValue.json(loaded_tables),
        }
    )
