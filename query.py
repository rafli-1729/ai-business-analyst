import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from openai import OpenAI

# load env
load_dotenv()

# =========================
# OPENROUTER CLIENT
# =========================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# =========================
# SUPABASE DATABASE
# =========================

DB_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DB_URL,
    connect_args={"sslmode": "require"}
)

# =========================
# USER QUESTION
# =========================

try:
    question = input("Enter your question: ")
except Exception as e:
    question = "What are the top 5 most profitable products?"

# =========================
# SCHEMA CONTEXT
# =========================

schema = """
Table: sales

Columns:
- order_date
- sales
- profit
- category
- product_name
- region
"""

# =========================
# PROMPT
# =========================

prompt = f"""
You are a PostgreSQL expert.

Convert the user question into SQL.

Return ONLY SQL.
Do not explain anything.

Schema:
{schema}

Question:
{question}
"""

# =========================
# GENERATE SQL
# =========================

response = client.chat.completions.create(
    model="inclusionai/ring-2.6-1t:free",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

generated_sql = response.choices[0].message.content

print("\nGenerated SQL:")
print(generated_sql)

forbidden = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE"
]

sql_upper = generated_sql.upper()

if any(word in sql_upper for word in forbidden):
    raise ValueError("Dangerous SQL detected!")

# =========================
# EXECUTE SQL
# =========================

with engine.connect() as conn:
    result = conn.execute(text(generated_sql))

    rows = result.fetchall()

# =========================
# SHOW RESULT
# =========================

print("\nQuery Result:")

for row in rows:
    print(row)