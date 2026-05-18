from orchestration.pipelines.warehouse_pipeline import run_warehouse_elt
from warehouse.schema import create_base_schemas
from warehouse.ingestion.config import load_ingestion_config

def main():
    config = load_ingestion_config()
    print("Ensuring base schemas exist...")
    create_base_schemas(config.database_url)
    print("Base schemas verified. Transformation pipeline is ready.")

    run_warehouse_elt(config.database_url)
    print("Transformation pipeline completed successfully.")

if __name__ == "__main__":
    main()