from orchestration.pipelines.warehouse_pipeline import run_warehouse_elt
from warehouse.ingestion.config import load_ingestion_config

from infra.database.engine import create_postgres_engine
from warehouse.quality.runner import run_quality_checks

def main():
    config = load_ingestion_config()
    run_warehouse_elt(config.database_url)

    engine = create_postgres_engine(
        config.database_url
    )

    validation_results = run_quality_checks(
        engine
    )

    print(validation_results)
    print("Transformation pipeline completed.")


if __name__ == "__main__":
    main()