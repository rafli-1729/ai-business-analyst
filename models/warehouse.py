from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class IngestionConfig:
    database_url: str
    dataset_slug: str = "olistbr/brazilian-ecommerce"
    bronze_schema: str = "bronze"
    ops_schema: str = "ops"
    chunk_size: int = 60000
    benchmark_top_tables: int = 2
    run_elt_after_ingest: bool = True


@dataclass(frozen=True)
class EltConfig:
    database_url: str
    sql_root: Path = Path("sql")
    layer_order: tuple[str, ...] = ("bronze", "silver", "gold")
    ops_schema: str = "ops"


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
