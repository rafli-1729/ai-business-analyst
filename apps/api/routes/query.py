import time

from fastapi import APIRouter, Depends, HTTPException

from apps.api.dependencies.settings import get_query_service, get_response_cache
from apps.api.schemas.request import QueryRequest
from apps.api.schemas.response import QueryResponse
from ai.services.result_formatter import dataframe_to_rows, infer_chart_type
from ai.summarization.narrative import summarize_query_result, summary_prompt_fingerprint
from services.observability import log_event
from services.query_service import QueryService
from services.response_cache import ResponseCache
from services.sql_guard import SqlValidationError


router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def run_query(
    payload: QueryRequest,
    service: QueryService = Depends(get_query_service),
    response_cache: ResponseCache = Depends(get_response_cache),
) -> QueryResponse:
    started_at = time.perf_counter()

    try:
        timings: dict[str, int] = {}
        phase_started_at = time.perf_counter()
        response_version = f"{summary_prompt_fingerprint()}:debug-{int(service.settings.debug)}"
        timings["summary_fingerprint_ms"] = int((time.perf_counter() - phase_started_at) * 1000)

        cached_response = None
        if not payload.refresh:
            phase_started_at = time.perf_counter()
            cached_response = response_cache.get(
                payload.question,
                service.schema_version,
                payload.row_limit,
                response_version=response_version,
            )
            timings["response_cache_lookup_ms"] = int((time.perf_counter() - phase_started_at) * 1000)
        else:
            timings["response_cache_lookup_ms"] = 0
            log_event(
                "response_cache_bypassed",
                reason="refresh_requested",
                summary_version=response_version,
            )
        if cached_response:
            log_event(
                "response_cache_hit",
                summary_version=response_version,
                question=payload.question[:200],
            )
            cached_response["cache_hit"] = True
            cached_response["execution_ms"] = int((time.perf_counter() - started_at) * 1000)
            cached_response["debug"] = service.settings.debug
            if service.settings.debug:
                cached_timings = cached_response.get("timings", {})
                cached_response["timings"] = {
                    **cached_timings,
                    **timings,
                    "api_total_ms": cached_response["execution_ms"],
                }
            else:
                cached_response["timings"] = {}
            return QueryResponse(**cached_response)

        phase_started_at = time.perf_counter()
        query_result = service.ask_with_metadata(
            payload.question,
            row_limit=payload.row_limit,
        )
        timings["query_service_call_ms"] = int((time.perf_counter() - phase_started_at) * 1000)
        sql = query_result["sql"]
        dataframe = query_result["dataframe"]

        phase_started_at = time.perf_counter()
        rows = dataframe_to_rows(dataframe, limit=payload.row_limit)
        timings["row_format_ms"] = int((time.perf_counter() - phase_started_at) * 1000)

        summary_started_at = time.perf_counter()
        summary = summarize_query_result(
            llm=service.llm,
            question=payload.question,
            sql=sql,
            rows=rows,
            max_tokens=service.settings.summary_max_tokens,
        )
        summary_ms = int((time.perf_counter() - summary_started_at) * 1000)
        timings["summary_ms"] = summary_ms
        log_event(
            "summary_generated",
            summary_version=response_version,
            summary_ms=summary_ms,
            question=payload.question[:200],
        )

        phase_started_at = time.perf_counter()
        chart_type = infer_chart_type(dataframe)
        timings["chart_infer_ms"] = int((time.perf_counter() - phase_started_at) * 1000)

        timings = {**query_result["timings"], **timings}
        execution_ms = int((time.perf_counter() - started_at) * 1000)
        timings["api_total_ms"] = execution_ms
        timings["total_ms"] = execution_ms

        response = QueryResponse(
            question=payload.question,
            sql=sql,
            summary=summary,
            rows=rows,
            chart_type=chart_type,
            row_count=len(dataframe.index),
            execution_ms=execution_ms,
            schema_version=service.schema_version,
            debug=service.settings.debug,
            is_truncated=query_result["is_truncated"],
            cache_hit=False,
            sql_cache_hit=query_result["sql_cache_hit"],
            timings=timings if service.settings.debug else {},
        )
        phase_started_at = time.perf_counter()
        response_cache.set(
            payload.question,
            service.schema_version,
            payload.row_limit,
            response.dict(),
            response_version=response_version,
        )
        if service.settings.debug:
            response.timings["response_cache_set_ms"] = int((time.perf_counter() - phase_started_at) * 1000)
        response.execution_ms = int((time.perf_counter() - started_at) * 1000)
        if service.settings.debug:
            response.timings["api_total_ms"] = response.execution_ms
            response.timings["total_ms"] = response.execution_ms
            log_event(
                "query_timing_breakdown",
                question=payload.question[:200],
                timings=response.timings,
            )
        return response

    except SqlValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        log_event("query_api_failed", error=str(exc), question=payload.question[:200])
        raise HTTPException(status_code=500, detail=f"Query execution failed: {exc}") from exc
