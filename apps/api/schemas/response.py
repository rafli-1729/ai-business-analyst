from typing import Any, Literal

from pydantic import BaseModel, Field


ChartType = Literal["bar", "line", "table"]


class QueryResponse(BaseModel):
    question: str
    sql: str
    summary: str
    rows: list[dict[str, Any]]
    chart_type: ChartType
    row_count: int
    execution_ms: int
    schema_version: str
    debug: bool = False
    is_truncated: bool = False
    cache_hit: bool = False
    sql_cache_hit: bool = False
