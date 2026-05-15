import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass(frozen=True)
class IngestionConfig:
    database_url: str
    dataset_slug: str = "olistbr/brazilian-ecommerce"
    bronze_schema: str = "bronze"
    ops_schema: str = "ops"
    chunk_size: int = 60000
    google_sheet_id: str = ""


@dataclass
class IngestionResult:
    source_file: str
    target_schema: str
    target_table: str
    status: str
    total_rows: int = 0
    inserted_rows: int = 0
    processed_chunks: int = 0
    write_modes: set[str] = field(default_factory=set)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "y"}


def load_ingestion_config() -> IngestionConfig:
    load_dotenv()

    database_url = os.getenv("INGESTER_DB_URL", "").strip()

    if not database_url:
        raise ValueError("Missing INGESTER_DB_URL")

    return IngestionConfig(
        database_url=database_url,
        dataset_slug=os.getenv("KAGGLE_DATASET_SLUG", "olistbr/brazilian-ecommerce"),
        chunk_size=int(os.getenv("INGEST_CHUNK_SIZE", "60000")),
        google_sheet_id=os.getenv("GOOGLE_SHEET_ID", ""),
    )