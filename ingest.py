import hashlib
import io
import math
import os
import time
import uuid
from datetime import datetime, timezone

import kagglehub
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from psycopg2 import sql
from tqdm import tqdm

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL, connect_args={"sslmode": "require"})
CHUNK_SIZE = 60000
BENCHMARK_TOP_TABLES = 2


def quote_ident(name: str) -> sql.Identifier:
    return sql.Identifier(name)


def copy_chunk_to_postgres(df: pd.DataFrame, table_name: str, sa_engine) -> None:
    if df.empty:
        return

    raw_conn = sa_engine.raw_connection()
    try:
        with raw_conn.cursor() as cursor:
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)

            column_identifiers = [quote_ident(col) for col in df.columns]
            copy_stmt = sql.SQL("COPY {} ({}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)").format(
                quote_ident(table_name),
                sql.SQL(", ").join(column_identifiers),
            )
            cursor.copy_expert(copy_stmt.as_string(raw_conn), buffer)
        raw_conn.commit()
    except Exception:
        raw_conn.rollback()
        raise
    finally:
        raw_conn.close()


def write_chunk_with_fallback(df: pd.DataFrame, table_name: str, sa_engine) -> str:
    try:
        copy_chunk_to_postgres(df, table_name, sa_engine)
        return "copy"
    except Exception as copy_error:
        print(f"COPY failed for table={table_name} chunk_rows={len(df.index)}. Falling back to to_sql append. Error: {copy_error}")
        df.to_sql(table_name, sa_engine, if_exists="append", index=False, method="multi", chunksize=CHUNK_SIZE)
        return "fallback_to_sql"


def benchmark_chunk_write(df: pd.DataFrame, table_name: str, sa_engine) -> None:
    benchmark_old_table = f"bench_old_{table_name}"
    benchmark_copy_table = f"bench_copy_{table_name}"

    start_old = time.perf_counter()
    df.head(0).to_sql(benchmark_old_table, sa_engine, if_exists="replace", index=False)
    df.to_sql(benchmark_old_table, sa_engine, if_exists="append", index=False, method="multi", chunksize=CHUNK_SIZE)
    old_elapsed = time.perf_counter() - start_old

    start_copy = time.perf_counter()
    df.head(0).to_sql(benchmark_copy_table, sa_engine, if_exists="replace", index=False)
    copy_chunk_to_postgres(df, benchmark_copy_table, sa_engine)
    copy_elapsed = time.perf_counter() - start_copy

    with sa_engine.begin() as conn:
        conn.execute(text(f'DROP TABLE IF EXISTS "{benchmark_old_table}"'))
        conn.execute(text(f'DROP TABLE IF EXISTS "{benchmark_copy_table}"'))

    print(f"Benchmark table={table_name}: old_method={old_elapsed:.2f}s vs copy_method={copy_elapsed:.2f}s (chunk_rows={len(df.index)})")


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


def has_successful_run(
    source_file: str,
    checksum: str,
    target_table: str
) -> bool:
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


def record_run(
    run_id: str,
    source_file: str,
    checksum: str,
    target_table: str,
    status: str,
    total_rows: int = 0,
    processed_chunks: int = 0,
    inserted_rows: int = 0
):
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

    file_rows = {}
    for file in files:
        file_path = f"{path}/{file}"
        file_rows[file] = max(sum(1 for _ in open(file_path, encoding="utf-8")) - 1, 0)

    largest_files = {f for f, _ in sorted(file_rows.items(), key=lambda item: item[1], reverse=True)[:BENCHMARK_TOP_TABLES]}

    for file in files:
        file_path = f"{path}/{file}"
        table_name = file.replace(".csv", "").replace("olist_", "").replace("_dataset", "")
        checksum = file_checksum(file_path)

        if has_successful_run(file, checksum, table_name):
            print(f"Skipping {table_name}: same source checksum already ingested.")
            continue

        run_id = str(uuid.uuid4())
        total_rows = file_rows[file]
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

                if first_chunk:
                    chunk.head(0).to_sql(staging_table, engine, if_exists="replace", index=False)

                    if file in largest_files:
                        benchmark_chunk_write(chunk, table_name, engine)

                write_mode = write_chunk_with_fallback(chunk, staging_table, engine)

                first_chunk = False
                processed_chunks += 1
                inserted_rows += len(chunk.index)
                if write_mode == "fallback_to_sql":
                    print(f"Chunk {processed_chunks} for table {table_name} persisted via fallback to_sql.")
                record_run(run_id, file, checksum, table_name, "running", total_rows=total_rows, processed_chunks=processed_chunks, inserted_rows=inserted_rows)

<<<<<<< HEAD
            # with engine.begin() as conn:
            #     conn.execute(text(f"truncate table {table_name} cascade"))
            #     conn.execute(text(f"alter table {staging_table} rename to {table_name}"))
=======
            with engine.begin() as conn:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
                conn.execute(text(f'ALTER TABLE "{staging_table}" RENAME TO "{table_name}"'))
>>>>>>> acbdf981ed6477e3f7bc3cfe0517cf27cba291d1

            record_run(run_id, file, checksum, table_name, "success", total_rows=total_rows, processed_chunks=processed_chunks, inserted_rows=inserted_rows)
        except Exception:
            record_run(run_id, file, checksum, table_name, "failed", total_rows=total_rows, processed_chunks=processed_chunks, inserted_rows=inserted_rows)
            raise

    print("\nAll tables ingestion run completed.")


if __name__ == "__main__":
    ingest_all()
