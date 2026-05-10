import hashlib
import math
import os
import uuid
from datetime import datetime, timezone

import kagglehub
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from tqdm import tqdm

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL, connect_args={"sslmode": "require"})
CHUNK_SIZE = 60000


def file_checksum(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_metadata_tables():
    ddl = """
    create table if not exists ingestion_runs (
      run_id text primary key,
      source_file text not null,
      source_checksum text not null,
      target_table text not null,
      status text not null,
      processed_chunks integer default 0,
      total_rows bigint,
      inserted_rows bigint,
      started_at timestamptz not null,
      finished_at timestamptz
    );
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))


def has_successful_run(source_file: str, checksum: str, target_table: str) -> bool:
    q = text(
        """
        select 1 from ingestion_runs
        where source_file=:source_file
          and source_checksum=:checksum
          and target_table=:target_table
          and status='success'
        limit 1
        """
    )
    with engine.connect() as conn:
        return conn.execute(q, {"source_file": source_file, "checksum": checksum, "target_table": target_table}).first() is not None


def record_run(run_id: str, source_file: str, checksum: str, target_table: str, status: str, total_rows: int = 0, processed_chunks: int = 0, inserted_rows: int = 0):
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(text("""
        insert into ingestion_runs(run_id, source_file, source_checksum, target_table, status, processed_chunks, total_rows, inserted_rows, started_at, finished_at)
        values(:run_id, :source_file, :source_checksum, :target_table, :status, :processed_chunks, :total_rows, :inserted_rows, :started_at, case when :status in ('success','failed') then :finished_at else null end)
        on conflict (run_id) do update set
          status=excluded.status,
          processed_chunks=excluded.processed_chunks,
          total_rows=excluded.total_rows,
          inserted_rows=excluded.inserted_rows,
          finished_at=excluded.finished_at
        """), {
            "run_id": run_id,
            "source_file": source_file,
            "source_checksum": checksum,
            "target_table": target_table,
            "status": status,
            "processed_chunks": processed_chunks,
            "total_rows": total_rows,
            "inserted_rows": inserted_rows,
            "started_at": now,
            "finished_at": now,
        })


def ingest_all():
    ensure_metadata_tables()

    path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
    files = os.listdir(path)

    for file in files:
        file_path = f"{path}/{file}"
        table_name = file.replace(".csv", "").replace("olist_", "").replace("_dataset", "")
        checksum = file_checksum(file_path)

        if has_successful_run(file, checksum, table_name):
            print(f"Skipping {table_name}: same source checksum already ingested.")
            continue

        run_id = str(uuid.uuid4())
        total_rows = max(sum(1 for _ in open(file_path, encoding="utf-8")) - 1, 0)
        total_chunks = math.ceil(total_rows / CHUNK_SIZE) if total_rows else 0

        print(f"\nIngesting table: {table_name}")
        record_run(run_id, file, checksum, table_name, "running", total_rows=total_rows)

        datetime_cols = {
            "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
            "order_delivered_customer_date", "order_estimated_delivery_date", "shipping_limit_date",
            "review_creation_date", "review_answer_timestamp"
        }

        inserted_rows = 0
        processed_chunks = 0

        try:
            staging_table = f"stg_{table_name}"
            first_chunk = True
            reader = pd.read_csv(file_path, chunksize=CHUNK_SIZE)

            for chunk in tqdm(reader, total=total_chunks, desc=table_name):
                chunk.columns = chunk.columns.str.lower().str.replace(" ", "_", regex=False)

                for col in datetime_cols.intersection(chunk.columns):
                    chunk[col] = pd.to_datetime(chunk[col], errors="coerce")

                chunk.to_sql(
                    staging_table,
                    engine,
                    if_exists="replace" if first_chunk else "append",
                    index=False,
                    method="multi",
                    chunksize=CHUNK_SIZE,
                )

                first_chunk = False
                processed_chunks += 1
                inserted_rows += len(chunk.index)
                record_run(run_id, file, checksum, table_name, "running", total_rows=total_rows, processed_chunks=processed_chunks, inserted_rows=inserted_rows)

            with engine.begin() as conn:
                conn.execute(text(f"drop table if exists {table_name}"))
                conn.execute(text(f"alter table {staging_table} rename to {table_name}"))

            record_run(run_id, file, checksum, table_name, "success", total_rows=total_rows, processed_chunks=processed_chunks, inserted_rows=inserted_rows)
        except Exception:
            record_run(run_id, file, checksum, table_name, "failed", total_rows=total_rows, processed_chunks=processed_chunks, inserted_rows=inserted_rows)
            raise

    print("\nAll tables ingestion run completed.")


if __name__ == "__main__":
    ingest_all()
