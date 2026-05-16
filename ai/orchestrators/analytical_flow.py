"""
Analytical flow for executing multi-step reasoning queries.

Coordinates multi-agent analytical workflows with planning, decomposition,
evidence collection, and synthesis.
"""

import time
from typing import Optional

from ai.orchestrators.analytical_orchestrator import AnalyticalOrchestrator
from ai.planners.semantic_planner import build_execution_plan
from ai.services.response_formatter_service import ResponseFormatterService
from ai.services.summarization_service import SummarizationService
from ai.caches.response_cache import ResponseCache
from ai.models.analytical_context import AnalyticalContext

from infra.observability.logger import log_event


def run_analytical_flow(
    question: str,
    orchestrator: AnalyticalOrchestrator,
    response_cache: ResponseCache,
    row_limit: Optional[int] = None,
    refresh: bool = False,
) -> dict:
    """
    Execute analytical flow with planning and multi-step reasoning.

    Orchestrates:
    1. Planning: Decompose question into execution plan
    2. Execution: Execute plan (simple or multi-step)
    3. Synthesis: Summarize results
    4. Caching: Cache complete response

    Args:
        question: User question
        orchestrator: AnalyticalOrchestrator for query execution
        response_cache: Response cache for caching results
        row_limit: Optional row limit
        refresh: Whether to bypass caching

    Returns:
        Response dictionary with results and metadata
    """

    execution_started = time.perf_counter()
    timings: dict[str, int] = {}

    response_version = (
        f"{SummarizationService.get_summary_fingerprint()}"
        f":debug-{int(orchestrator.settings.debug)}"
    )

    # PHASE 1: RESPONSE CACHE LOOKUP
    if not refresh:
        cached_response = response_cache.get(
            question=question,
            schema_version=orchestrator.schema_version,
            row_limit=row_limit,
            response_version=response_version,
        )

        if cached_response:
            cached_response["cache_hit"] = True
            log_event(
                "analytical_flow_response_cache_hit",
                question=question[:200],
            )
            return cached_response

    # PHASE 2: PLANNING
    planning_started = time.perf_counter()

    execution_plan = build_execution_plan(question)

    timings["planning_ms"] = int(
        (time.perf_counter() - planning_started) * 1000
    )

    log_event(
        "analytical_flow_plan_built",
        intent=execution_plan.get("intent"),
        requires_reasoning=execution_plan.get("requires_reasoning"),
    )

    # PHASE 3: EXECUTION - Simple Flow
    if not execution_plan.get("requires_reasoning"):
        return _execute_simple_flow(
            question=question,
            orchestrator=orchestrator,
            response_cache=response_cache,
            row_limit=row_limit,
            response_version=response_version,
            initial_timings=timings,
            started_at=execution_started,
        )

    # PHASE 3: EXECUTION - Multi-Step Reasoning Flow
    else:
        return _execute_reasoning_flow(
            question=question,
            execution_plan=execution_plan,
            orchestrator=orchestrator,
            response_cache=response_cache,
            row_limit=row_limit,
            response_version=response_version,
            initial_timings=timings,
            started_at=execution_started,
        )


def _execute_simple_flow(
    question: str,
    orchestrator: AnalyticalOrchestrator,
    response_cache: ResponseCache,
    row_limit: Optional[int],
    response_version: str,
    initial_timings: dict[str, int],
    started_at: float,
) -> dict:
    """
    Execute simple (non-reasoning) analytical query.

    Flow:
    1. Execute query via orchestrator
    2. Format results
    3. Summarize
    4. Cache response
    """

    # Execute query via orchestrator
    result = orchestrator.execute_query(
        question=question,
        row_limit=row_limit or 100,
    )

    # Format rows for response
    formatter = ResponseFormatterService()
    rows = formatter.dataframe_to_rows(
        result.dataframe,
        limit=row_limit or 100,
    )

    # Build response
    response = {
        "question": result.question,
        "sql": result.sql,
        "rows": rows,
        "row_count": len(rows),
        "summary": result.summary,
        "chart_type": result.metadata.get("chart_type", "table"),
        "cache_hit": False,
        "is_truncated": result.is_truncated,
        "timings": {
            **initial_timings,
            **result.timings,
        },
        "execution_ms": int(
            (time.perf_counter() - started_at) * 1000
        ),
        "schema_version": result.metadata.get("schema_version"),
        "model": result.metadata.get("model"),
    }

    # Cache response
    response_cache.set(
        question=question,
        schema_version=orchestrator.schema_version,
        row_limit=row_limit,
        payload=response,
        response_version=response_version,
    )

    log_event(
        "analytical_flow_simple_completed",
        question=question[:200],
        execution_ms=response["execution_ms"],
    )

    return response


def _execute_reasoning_flow(
    question: str,
    execution_plan: dict,
    orchestrator: AnalyticalOrchestrator,
    response_cache: ResponseCache,
    row_limit: Optional[int],
    response_version: str,
    initial_timings: dict[str, int],
    started_at: float,
) -> dict:
    """
    Execute multi-step reasoning analytical flow.

    Flow:
    1. For each task in plan:
       a. Build analytical context
       b. Execute query via orchestrator
       c. Collect findings
    2. Synthesize findings into summary
    3. Cache response
    """

    findings = []

    # Execute each task in the plan
    for task in execution_plan.get("tasks", []):
        task_started = time.perf_counter()

        # Build context for this task
        context = AnalyticalContext(
            intent=execution_plan.get("intent", "diagnostic"),
            agent=task.get("agent", "diagnostic"),
            mart=task.get("mart", "analytical"),
            question=task.get("question", question),
            focus_areas=[],
        )

        # Execute task via orchestrator
        task_result = orchestrator.execute_query(
            question=task.get("question", question),
            row_limit=row_limit or 10,
            context=context,
        )

        task_ms = int((time.perf_counter() - task_started) * 1000)

        # Format results for this task
        formatter = ResponseFormatterService()
        rows = formatter.dataframe_to_rows(
            task_result.dataframe,
            limit=10,
        )

        # Collect finding
        finding = {
            "agent": context.agent,
            "mart": context.mart,
            "sql": task_result.sql,
            "rows": rows,
            "row_count": len(rows),
            "execution_ms": task_ms,
        }

        findings.append(finding)

        log_event(
            "analytical_flow_task_completed",
            agent=context.agent,
            task_ms=task_ms,
        )

    # Synthesize findings with summarization
    summarizer = SummarizationService(orchestrator.llm)

    synthesis_started = time.perf_counter()

    summary = summarizer.summarize_query_result(
        question=question,
        sql="MULTI_STEP_REASONING",
        rows=findings,
        max_tokens=orchestrator.settings.summary_max_tokens,
    )

    synthesis_ms = int(
        (time.perf_counter() - synthesis_started) * 1000
    )

    # Build response
    response = {
        "question": question,
        "summary": summary,
        "evidence": findings,
        "finding_count": len(findings),
        "cache_hit": False,
        "timings": {
            **initial_timings,
            "synthesis_ms": synthesis_ms,
        },
        "execution_ms": int(
            (time.perf_counter() - started_at) * 1000
        ),
        "schema_version": orchestrator.schema_version,
    }

    # Cache response
    response_cache.set(
        question=question,
        schema_version=orchestrator.schema_version,
        row_limit=row_limit,
        payload=response,
        response_version=response_version,
    )

    log_event(
        "analytical_flow_reasoning_completed",
        question=question[:200],
        finding_count=len(findings),
        execution_ms=response["execution_ms"],
    )

    return response
