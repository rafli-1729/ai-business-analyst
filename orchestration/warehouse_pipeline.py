from pathlib import Path

from ingestion.loader import BronzeIngestor
from models.warehouse import EltConfig, IngestionConfig
from warehouse.elt_runner import run_elt
from warehouse.schema import create_base_schemas


def run_ingestion_pipeline(config: IngestionConfig) -> list:
    create_base_schemas(config.database_url)
    ingestor = BronzeIngestor(config)
    results = ingestor.ingest_dataset()

    if config.run_elt_after_ingest:
        run_warehouse_elt(config.database_url)

    return results


def run_warehouse_elt(database_url: str, sql_root: Path | None = None) -> dict:
    root = sql_root or Path(__file__).resolve().parent.parent / "sql"

    return run_elt(
        EltConfig(
            database_url=database_url,
            sql_root=root,
        )
    )
