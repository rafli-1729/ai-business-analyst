import math
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from tqdm import tqdm

from infra.database.engine import (
    create_postgres_engine,
    quoted_identifier,
    quoted_table,
)
from warehouse.ingestion.config import (
    IngestionConfig,
    IngestionResult,
)
from warehouse.ingestion.metadata.metadata import (
    ensure_ingestion_metadata,
    file_checksum,
    has_successful_run,
    record_ingestion_run,
    table_exists,
)
from warehouse.ingestion.registry import TABLE_REGISTRY
from warehouse.ingestion.routing.schema_router import (
    resolve_target_schema,
)
from warehouse.ingestion.sources.kaggle import KaggleSource
from warehouse.ingestion.sources.google_sheets import (
    GoogleSheetsSource,
)
from warehouse.ingestion.writer.postgres_copy import (
    copy_chunk_to_postgres,
)

from warehouse.ingestion.sources.google_sheets import (
    GoogleSheetsSource,
)


class BronzeIngestor:
    """
    Metadata-driven ingestion orchestrator.

    Responsibilities:
    - resolve sources dynamically
    - resolve target schemas dynamically
    - orchestrate chunk ingestion
    - maintain ingestion metadata
    - preserve raw structure
    """

    def __init__(self, config: IngestionConfig):
        self.config = config

        self.engine = create_postgres_engine(
            config.database_url
        )

        self.sources = {
            "kaggle": KaggleSource(
                dataset_slug=config.dataset_slug
            ),

            "google_sheets": GoogleSheetsSource(
                spreadsheet_id=config.google_sheet_id
            ),
        }

    def ingest_dataset(self) -> list[IngestionResult]:
        self._ensure_required_schemas()

        ensure_ingestion_metadata(
            self.engine,
            self.config.ops_schema,
        )

        ingestion_plan = self._build_ingestion_plan()

        results: list[IngestionResult] = []

        for plan in ingestion_plan:
            results.append(
                self.ingest_file(
                    source_path=plan["source_path"],
                    table_name=plan["table_name"],
                    target_schema=plan["target_schema"],
                    total_rows=plan["total_rows"],
                )
            )

        print("\nIngestion completed.")

        return results

    def _build_ingestion_plan(self) -> list[dict]:
        plans: list[dict] = []

        for source_type, source in self.sources.items():
            dataset_path = source.fetch()
            source_files = source.list_csv_files(dataset_path)

            for source_path in source_files:
                table_name = self._table_name_from_path(
                    source_path
                )

                if table_name not in TABLE_REGISTRY:
                    print(
                        f"Skipping unregistered table: {table_name}"
                    )
                    continue

                registry = TABLE_REGISTRY[table_name]

                if registry["source_type"] != source_type:
                    continue

                plans.append(
                    {
                        "source_path": source_path,
                        "table_name": table_name,
                        "target_schema": resolve_target_schema(
                            table_name
                        ),
                        "total_rows": self._estimate_csv_rows(
                            source_path
                        ),
                    }
                )

        return plans

    def ingest_file(
        self,
        source_path: Path,
        table_name: str,
        target_schema: str,
        total_rows: int,
    ) -> IngestionResult:

        checksum = file_checksum(source_path)

        if (
            has_successful_run(
                self.engine,
                source_path.name,
                checksum,
                target_schema,
                table_name,
                self.config.ops_schema,
            )
            and
            table_exists(
                self.engine,
                target_schema,
                table_name,
            )
        ):
            print(
                f"\nSkipping {target_schema}.{table_name}: "
                f"source checksum already ingested."
            )

            return IngestionResult(
                source_file=source_path.name,
                target_schema=target_schema,
                target_table=table_name,
                status="skipped",
                total_rows=total_rows,
            )

        run_id = str(uuid.uuid4())

        total_chunks = (
            math.ceil(total_rows / self.config.chunk_size)
            if total_rows
            else 0
        )

        short_id = uuid.uuid4().hex[:8]
        safe_table_name = table_name[:40]

        staging_table = (
            f"stg_{safe_table_name}_{short_id}"
        )

        record_ingestion_run(
            self.engine,
            run_id,
            source_path.name,
            checksum,
            target_schema,
            table_name,
            "running",
            total_rows=total_rows,
            ops_schema=self.config.ops_schema,
        )

        inserted_rows = 0
        processed_chunks = 0

        print(
            f"\nIngesting {target_schema}.{table_name}"
        )

        try:
            reader = pd.read_csv(
                source_path,
                chunksize=self.config.chunk_size,
            )

            first_chunk = True

            for chunk in tqdm(
                reader,
                total=total_chunks,
                desc=table_name,
            ):

                chunk = self._prepare_chunk(
                    chunk=chunk,
                    source_file=source_path.name,
                    checksum=checksum,
                    run_id=run_id,
                )

                if first_chunk:
                    self._create_staging_table(
                        chunk=chunk,
                        schema_name=target_schema,
                        staging_table=staging_table,
                    )

                    first_chunk = False

                copy_chunk_to_postgres(
                    df=chunk,
                    schema_name=target_schema,
                    table_name=staging_table,
                    engine=self.engine,
                )

                processed_chunks += 1
                inserted_rows += len(chunk.index)

            self._swap_staging_table(
                target_schema=target_schema,
                staging_table=staging_table,
                target_table=table_name,
            )

            record_ingestion_run(
                self.engine,
                run_id,
                source_path.name,
                checksum,
                target_schema,
                table_name,
                "success",
                total_rows=total_rows,
                processed_chunks=processed_chunks,
                inserted_rows=inserted_rows,
                ops_schema=self.config.ops_schema,
            )

            return IngestionResult(
                source_file=source_path.name,
                target_schema=target_schema,
                target_table=table_name,
                status="success",
                total_rows=total_rows,
                processed_chunks=processed_chunks,
                inserted_rows=inserted_rows,
                write_modes={"copy"},
            )

        except Exception:

            record_ingestion_run(
                self.engine,
                run_id,
                source_path.name,
                checksum,
                target_schema,
                table_name,
                "failed",
                total_rows=total_rows,
                processed_chunks=processed_chunks,
                inserted_rows=inserted_rows,
                ops_schema=self.config.ops_schema,
            )

            raise

    def _prepare_chunk(
        self,
        chunk: pd.DataFrame,
        source_file: str,
        checksum: str,
        run_id: str,
    ) -> pd.DataFrame:

        chunk.columns = (
            chunk.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
        )

        chunk["_ingested_at"] = datetime.now(
            timezone.utc
        )

        chunk["_source_file"] = source_file
        chunk["_source_checksum"] = checksum
        chunk["_ingestion_run_id"] = run_id

        return chunk

    def _create_staging_table(
        self,
        chunk: pd.DataFrame,
        schema_name: str,
        staging_table: str,
    ) -> None:

        chunk.head(0).to_sql(
            staging_table,
            self.engine,
            schema=schema_name,
            if_exists="replace",
            index=False,
        )

    def _swap_staging_table(
        self,
        target_schema: str,
        staging_table: str,
        target_table: str,
    ) -> None:

        with self.engine.begin() as conn:
            conn.execute(
                text(
                    f"""
                    DROP TABLE IF EXISTS
                    {quoted_table(target_schema, target_table)};

                    ALTER TABLE
                    {quoted_table(target_schema, staging_table)}
                    RENAME TO {quoted_identifier(target_table)};
                    """
                )
            )

    def _ensure_required_schemas(self) -> None:

        required_schemas = {
            config["target_schema"]
            for config in TABLE_REGISTRY.values()
        }

        with self.engine.begin() as conn:
            for schema_name in required_schemas:
                conn.execute(
                    text(
                        f"""
                        CREATE SCHEMA IF NOT EXISTS
                        {quoted_identifier(schema_name)}
                        """
                    )
                )

    @staticmethod
    def _table_name_from_path(path: Path) -> str:
        return (
            path.name
            .replace(".csv", "")
            .replace("olist_", "")
            .replace("_dataset", "")
        )

    @staticmethod
    def _estimate_csv_rows(path: Path) -> int:
        with path.open(encoding="utf-8") as file:
            return max(sum(1 for _ in file) - 1, 0)
