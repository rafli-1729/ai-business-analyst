import streamlit as st

from services.config import get_settings
from services.query_service import QueryService

st.title("AI Business Analyst")

question = st.text_input("Ask your business question")

if question:
    try:
        service = QueryService(get_settings())
        sql, df_result = service.ask(question)
        st.code(sql, language="sql")
        st.dataframe(df_result)
    except Exception as e:
        st.error(str(e))
