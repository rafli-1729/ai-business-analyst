import os
import streamlit as st
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from openai import OpenAI

from schema import SCHEMA

load_dotenv()

# ======================
# OPENROUTER
# ======================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# ======================
# DATABASE
# ======================

engine = create_engine(
    os.getenv("DATABASE_URL"),
    connect_args={"sslmode": "require"}
)

# ======================
# UI
# ======================

st.title("AI Business Analyst")

question = st.text_input(
    "Ask your business question"
)

if question:
    prompt = f"""
    You are a PostgreSQL expert.

    Convert the user question into SQL.

    Return ONLY SQL Query without backticks and explanations.

    Schema:
    {SCHEMA}

    Question:
    {question}
    """

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
    sql_upper = generated_sql.upper()

    forbidden_keywords = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE"
    ]

    if any(keyword in sql_upper for keyword in forbidden_keywords):
        st.error("Dangerous SQL detected!")
    else:
        st.code(generated_sql, language="sql")
        with engine.connect() as conn:
            result = conn.execute(text(generated_sql))
            rows = result.fetchall()
            columns = result.keys()

        df_result = pd.DataFrame(
            rows,
            columns=columns
        )

        st.dataframe(df_result)