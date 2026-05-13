import os

from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, asset

from models.warehouse import IngestionConfig
from orchestration.warehouse_pipeline import run_ingestion_pipeline


@asset(group_name="bronze", compute_kind="python")
def bronze_olist_sources(context: AssetExecutionContext) -> MaterializeResult:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise ValueError("Missing DATABASE_URL")

    results = run_ingestion_pipeline(
        IngestionConfig(
            database_url=database_url,
            run_elt_after_ingest=False,
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
