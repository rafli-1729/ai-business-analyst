import os

from dotenv import load_dotenv

from models.warehouse import IngestionConfig


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "y"}


def load_ingestion_config() -> IngestionConfig:
    load_dotenv()

    database_url = os.getenv("DATABASE_URL", "").strip()

    if not database_url:
        raise ValueError("Missing DATABASE_URL")

    return IngestionConfig(
        database_url=database_url,
        dataset_slug=os.getenv("KAGGLE_DATASET_SLUG", "olistbr/brazilian-ecommerce"),
        bronze_schema=os.getenv("BRONZE_SCHEMA", "bronze"),
        chunk_size=int(os.getenv("INGEST_CHUNK_SIZE", "60000")),
        benchmark_top_tables=int(os.getenv("BENCHMARK_TOP_TABLES", "2")),
        run_elt_after_ingest=_env_bool("RUN_ELT_AFTER_INGEST", True),
    )
