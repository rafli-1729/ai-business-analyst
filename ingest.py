from ingestion.config import load_ingestion_config
from orchestration.warehouse_pipeline import run_ingestion_pipeline


def main() -> None:
    config = load_ingestion_config()
    results = run_ingestion_pipeline(config)

    successful = sum(1 for result in results if result.status == "success")
    skipped = sum(1 for result in results if result.status == "skipped")

    print("\nIngestion pipeline completed.")
    print(f"successful_tables={successful}")
    print(f"skipped_tables={skipped}")


if __name__ == "__main__":
    main()
