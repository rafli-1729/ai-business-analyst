from sqlalchemy import create_engine
import pandas as pd

import os
from dotenv import load_dotenv

import kagglehub

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DB_URL,
    connect_args={"sslmode": "require"}
)

path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
files = os.listdir(path)

from tqdm import tqdm
import math

CHUNK_SIZE = 60000

for file in files:

    file_path = f"{path}/{file}"

    table_name = (
        file
        .replace(".csv", "")
        .replace("olist_", "")
        .replace("_dataset", "")
    )

    print(f"\nIngesting table: {table_name}")

    # estimate total rows
    total_rows = sum(1 for _ in open(file_path, encoding="utf-8")) - 1

    total_chunks = math.ceil(total_rows / CHUNK_SIZE)

    first_chunk = True

    reader = pd.read_csv(
        file_path,
        chunksize=CHUNK_SIZE
    )

    for chunk in tqdm(
        reader,
        total=total_chunks,
        desc=table_name
    ):

        # clean column names
        chunk.columns = (
            chunk.columns
            .str.lower()
            .str.replace(" ", "_")
        )

        # datetime conversion
        datetime_cols = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "shipping_limit_date",
            "review_creation_date",
            "review_answer_timestamp"
        ]

        for col in datetime_cols:
            if col in chunk.columns:
                chunk[col] = pd.to_datetime(
                    chunk[col],
                    errors="coerce"
                )

        # write chunk
        chunk.to_sql(
            table_name,
            engine,
            if_exists="replace" if first_chunk else "append",
            index=False,
            method="multi",
            chunksize=CHUNK_SIZE
        )

        first_chunk = False

print("\nAll tables successfully ingested.")