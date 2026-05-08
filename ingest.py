from sqlalchemy import create_engine
import pandas as pd

import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DB_URL,
    connect_args={"sslmode": "require"}
)

df = pd.read_csv("data/sales.csv", encoding="latin1")
df.columns = (
    df.columns
    .str.lower()
    .str.replace(" ", "_")
)

df["order_date"] = pd.to_datetime(df["order_date"], format="mixed")
df["ship_date"] = pd.to_datetime(df["ship_date"], format="mixed")

df.to_sql(
    "sales",
    engine,
    if_exists="replace",
    index=False
)

print("Data berhasil masuk ke Supabase")