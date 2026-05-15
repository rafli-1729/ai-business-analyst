from warehouse.ingestion.loader import BronzeIngestor
from warehouse.ingestion.config import (
    IngestionConfig,
    load_ingestion_config
)
from orchestration.pipelines.transformation_pipeline import run_warehouse_elt
from warehouse.schema import create_base_schemas


def run_ingestion_pipeline(config: IngestionConfig) -> list:
    create_base_schemas(config.database_url)

    ingestor = BronzeIngestor(config)
    results = ingestor.ingest_dataset()

    return results


def main():
    config  = load_ingestion_config()
    results = run_ingestion_pipeline(config)

    successful = sum(
        1 for result in results
        if result.status == "success"
    )

    skipped = sum(
        1 for result in results
        if result.status == "skipped"
    )

    print("\nIngestion pipeline completed.")
    print(f"successful_tables = {successful}")
    print(f"skipped_tables    = {skipped}")


if __name__ == "__main__":
    main()