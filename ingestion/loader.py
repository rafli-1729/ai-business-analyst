import math
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from tqdm import tqdm

from ingestion.metadata import (
    ensure_ingestion_metadata,
    file_checksum,
    has_successful_run,
    record_ingestion_run,
)
from ingestion.postgres_copy import copy_chunk_to_postgres
from ingestion.source import (
    download_dataset,
    estimate_csv_rows,
    list_csv_files,
    table_name_from_source_file,
)
from models.warehouse import IngestionConfig, IngestionResult
from services.sql_execution import create_postgres_engine
from utils.sql import quoted_identifier, quoted_table


class BronzeIngestor:
    """
    Bronze ingestion layer.

    Responsibilities:
    - ingest raw CSV files into PostgreSQL bronze schema
    - preserve raw structure
    - add ingestion metadata
    - use COPY-based ingestion
    - maintain ingestion lineage + idempotency
    """

    def __init__(self, config: IngestionConfig):
        self.config = config
        self.engine = create_postgres_engine(config.database_url)

    def ingest_dataset(self) -> list[IngestionResult]:
        self._ensure_bronze_schema()
        ensure_ingestion_metadata(self.engine, self.config.ops_schema)

        dataset_path = download_dataset(self.config.dataset_slug)
        source_files = list_csv_files(dataset_path)

        file_rows = {
            path.name: estimate_csv_rows(path)
            for path in source_files
        }

        results: list[IngestionResult] = []

        for source_path in source_files:
            results.append(
                self.ingest_file(
                    source_path=source_path,
                    total_rows=file_rows[source_path.name],
                )
            )

        print("\nBronze ingestion completed.")

        return results

    def ingest_file(
        self,
        source_path: Path,
        total_rows: int,
    ) -> IngestionResult:

        target_table = table_name_from_source_file(source_path)
        checksum = file_checksum(source_path)

        if has_successful_run(
            self.engine,
            source_path.name,
            checksum,
            self.config.bronze_schema,
            target_table,
            self.config.ops_schema,
        ):
            print(
                f"\nSkipping bronze.{target_table}: "
                f"source checksum already ingested."
            )

            return IngestionResult(
                source_file=source_path.name,
                target_schema=self.config.bronze_schema,
                target_table=target_table,
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
        safe_table_name = target_table[:40]

        staging_table = f"stg_{safe_table_name}_{short_id}"

        record_ingestion_run(
            self.engine,
            run_id,
            source_path.name,
            checksum,
            self.config.bronze_schema,
            target_table,
            "running",
            total_rows=total_rows,
            ops_schema=self.config.ops_schema,
        )

        inserted_rows = 0
        processed_chunks = 0

        print(f"\nIngesting bronze table: {target_table}")

        try:
            reader = pd.read_csv(
                source_path,
                chunksize=self.config.chunk_size,
            )

            first_chunk = True

            for chunk in tqdm(
                reader,
                total=total_chunks,
                desc=target_table,
            ):

                chunk = self._prepare_bronze_chunk(
                    chunk=chunk,
                    source_file=source_path.name,
                    checksum=checksum,
                    run_id=run_id,
                )

                if first_chunk:
                    self._create_staging_table(
                        chunk=chunk,
                        staging_table=staging_table,
                    )

                    first_chunk = False

                    copy_chunk_to_postgres(
                        df=chunk,
                        schema_name=self.config.bronze_schema,
                        table_name=staging_table,
                        engine=self.engine,
                    )

                processed_chunks += 1
                inserted_rows += len(chunk.index)

                # reduce metadata write noise
                if processed_chunks % 5 == 0:
                    record_ingestion_run(
                        self.engine,
                        run_id,
                        source_path.name,
                        checksum,
                        self.config.bronze_schema,
                        target_table,
                        "running",
                        total_rows=total_rows,
                        processed_chunks=processed_chunks,
                        inserted_rows=inserted_rows,
                        ops_schema=self.config.ops_schema,
                    )

            self._swap_staging_table(
                staging_table=staging_table,
                target_table=target_table,
            )

            record_ingestion_run(
                self.engine,
                run_id,
                source_path.name,
                checksum,
                self.config.bronze_schema,
                target_table,
                "success",
                total_rows=total_rows,
                processed_chunks=processed_chunks,
                inserted_rows=inserted_rows,
                ops_schema=self.config.ops_schema,
            )

            return IngestionResult(
                source_file=source_path.name,
                target_schema=self.config.bronze_schema,
                target_table=target_table,
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
                self.config.bronze_schema,
                target_table,
                "failed",
                total_rows=total_rows,
                processed_chunks=processed_chunks,
                inserted_rows=inserted_rows,
                ops_schema=self.config.ops_schema,
            )

            raise

    def _ensure_bronze_schema(self) -> None:

        with self.engine.begin() as conn:
            conn.execute(
                text(
                    f"""
                    CREATE SCHEMA IF NOT EXISTS
                    {quoted_identifier(self.config.bronze_schema)}
                    """
                )
            )

    def _prepare_bronze_chunk(
        self,
        chunk: pd.DataFrame,
        source_file: str,
        checksum: str,
        run_id: str,
    ) -> pd.DataFrame:

        # mutate directly for memory efficiency
        chunk.columns = (
            chunk.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_", regex=False)
        )

        chunk["_ingested_at"] = datetime.now(timezone.utc)
        chunk["_source_file"] = source_file
        chunk["_source_checksum"] = checksum
        chunk["_ingestion_run_id"] = run_id

        return chunk

    def _create_staging_table(
        self,
        chunk: pd.DataFrame,
        staging_table: str,
    ) -> None:
        """
        Create staging table schema using pandas dtype inference once.
        """

        chunk.head(0).to_sql(
            staging_table,
            self.engine,
            schema=self.config.bronze_schema,
            if_exists="replace",
            index=False,
        )

    def _swap_staging_table(
        self,
        staging_table: str,
        target_table: str,
    ) -> None:

        backup_table = f"{target_table}_old"

        with self.engine.begin() as conn:

            conn.execute(
                text(
                    f"""
                    DROP TABLE IF EXISTS
                    {quoted_table(self.config.bronze_schema, backup_table)}
                    CASCADE
                    """
                )
            )

            conn.execute(
                text(
                    f"""
                    ALTER TABLE IF EXISTS
                    {quoted_table(self.config.bronze_schema, target_table)}
                    RENAME TO {quoted_identifier(backup_table)}
                    """
                )
            )

            conn.execute(
                text(
                    f"""
                    ALTER TABLE
                    {quoted_table(self.config.bronze_schema, staging_table)}
                    RENAME TO {quoted_identifier(target_table)}
                    """
                )
            )

            conn.execute(
                text(
                    f"""
                    DROP TABLE IF EXISTS
                    {quoted_table(self.config.bronze_schema, backup_table)}
                    CASCADE
                    """
                )
            )