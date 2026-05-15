from ai.services.result_formatter import (
    infer_chart_type,
)


def build_query_response(
    question: str,
    sql: str,
    rows: list[dict],
    summary: str,
    timings: dict,
    query_result: dict,
    service,
    execution_ms: int,
):

    dataframe = query_result[
        "dataframe"
    ]

    return {
        "question": question,
        "sql": sql,
        "rows": rows,
        "row_count": len(rows),
        "summary": summary,
        "chart_type": infer_chart_type(
            dataframe
        ),
        "cache_hit": query_result.get(
            "sql_cache_hit",
            False,
        ),
        "is_truncated": query_result.get(
            "is_truncated",
            False,
        ),
        "timings": {
            **timings,
            **query_result.get(
                "timings",
                {},
            ),
            "execution_ms": execution_ms,
        },
        "execution_ms": execution_ms,
        "schema_version": (
            service.schema_version
        ),
        "model": (
            service.settings.llm_model
        ),
    }