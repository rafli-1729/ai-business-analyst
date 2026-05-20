from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from apps.api.dependencies.settings import (
    get_orchestrator,
)

from apps.api.schemas.request import (
    QueryRequest,
)

from apps.api.schemas.response import (
    QueryResponse,
)

from core_analytics.analytics.engine import (
    AnalyticsEngine,
)

from infra.observability.logger import (
    log_event,
)

router = APIRouter(tags=["query"])


@router.post(
    "/query",
    response_model=QueryResponse,
)
async def run_query(
    payload: QueryRequest,
    orchestrator: AnalyticsEngine = Depends(
        get_orchestrator
    ),
):
    """
    Execute an analytical query.

    Orchestrates query planning, multi-step reasoning if needed,
    SQL generation, validation, execution, and summarization.
    """

    try:
        # Run analytics engine (which uses LangGraph planner internally)
        result_data = await orchestrator.run(payload.question)
        
        # Transform artifacts into QueryResponse
        artifacts = result_data.get("artifacts", [])
        
        # 1. Find summary
        summary = "No summary generated."
        for a in artifacts:
            if a.type in ["executive_summary", "unified_executive_summary"]:
                summary = a.content
                break
                
        # 2. Find SQL and rows (this might need better tool logging)
        sql_query = "-- SQL query not captured in artifacts"
        rows = []
        chart_type = "table"
        
        for a in artifacts:
            if a.type == "sql":
                sql_query = a.content
            elif a.type == "table":
                # Assuming content is markdown or list of dicts
                if isinstance(a.content, list):
                    rows = a.content
                elif isinstance(a.content, str):
                    summary += f"\n\nData Table:\n{a.content}"
            elif a.type == "chart":
                chart_type = "bar" # Default for now
                if isinstance(a.content, dict):
                    chart_type = a.content.get("type", "bar")
                    # CRITICAL FIX: Extract chart data so frontend can render it
                    if not rows and "data" in a.content:
                        rows = a.content["data"]

        return QueryResponse(
            question=payload.question,
            sql=sql_query,
            summary=summary,
            rows=rows,
            chart_type=chart_type,
            row_count=len(rows),
            execution_ms=0,
            schema_version="1.0.0",
        )

    except Exception as exc:

        log_event(
            "query_api_failed",
            error=str(exc),
            question=payload.question[:200],
        )

        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {exc}",
        ) from exc
