from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from apps.api.dependencies.settings import (
    get_query_service,
    get_response_cache,
)

from apps.api.schemas.request import (
    QueryRequest,
)

from apps.api.schemas.response import (
    QueryResponse,
)

from ai.orchestration.analytical_flow import (
    run_analytical_flow,
)

from ai.services.query_service import (
    QueryService,
)

from ai.services.response_cache import (
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
    service: QueryService = Depends(
        get_query_service
    ),
    response_cache: ResponseCache = Depends(
        get_response_cache
    ),
):

    try:

        result = run_analytical_flow(
            payload=payload,
            service=service,
            response_cache=response_cache,
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