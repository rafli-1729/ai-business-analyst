from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from apps.api.dependencies.settings import (
    get_orchestrator,
    get_response_cache,
)

from apps.api.schemas.request import (
    QueryRequest,
)

from apps.api.schemas.response import (
    QueryResponse,
)

from ai.orchestrators.analytical_flow import (
    run_analytical_flow,
)

from ai.orchestrators.analytical_orchestrator import (
    AnalyticalOrchestrator,
)

from ai.caches.response_cache import (
    ResponseCache,
)

from ai.services.sql_guard import (
    SqlValidationError,
)

from infra.observability.logger import (
    log_event,
)

router = APIRouter(tags=["query"])


@router.post(
    "/query",
    response_model=QueryResponse,
)
def run_query(
    payload: QueryRequest,
    orchestrator: AnalyticalOrchestrator = Depends(
        get_orchestrator
    ),
    response_cache: ResponseCache = Depends(
        get_response_cache
    ),
):
    """
    Execute an analytical query.

    Orchestrates query planning, multi-step reasoning if needed,
    SQL generation, validation, execution, and summarization.
    """

    try:
        # Run analytical flow with planning and potential multi-step reasoning
        result = run_analytical_flow(
            question=payload.question,
            orchestrator=orchestrator,
            response_cache=response_cache,
            row_limit=payload.row_limit,
            refresh=payload.refresh,
        )

        return QueryResponse(**result)

    except SqlValidationError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

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
