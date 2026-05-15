import time

from ai.orchestration.response_builder import (
    build_query_response,
)

from ai.planners.semantic_planner import (
    build_execution_plan,
)

from ai.services.result_formatter import (
    dataframe_to_rows,
    infer_chart_type,
)

from ai.summarization.narrative import (
    summarize_query_result,
    summary_prompt_fingerprint,
)

from infra.observability.logger import (
    log_event,
)


def run_analytical_flow(
    payload,
    service,
    response_cache,
):

    started_at = time.perf_counter()

    timings: dict[str, int] = {}

    response_version = (
        f"{summary_prompt_fingerprint()}"
        f":debug-{int(service.settings.debug)}"
    )

    cached_response = response_cache.get(
        question=payload.question,
        schema_version=service.schema_version,
        row_limit=payload.row_limit,
        response_version=response_version,
    )

    # CACHE LOOKUP
    if not payload.refresh:

        cached_response = response_cache.get(
            payload.question,
            service.schema_version,
            payload.row_limit,
            response_version=response_version,
        )

        if cached_response:

            cached_response["cache_hit"] = True

            return cached_response

    # PLANNING
    planning_started_at = (
        time.perf_counter()
    )

    execution_plan = build_execution_plan(
        payload.question
    )

    timings["planning_ms"] = int(
        (
            time.perf_counter()
            - planning_started_at
        ) * 1000
    )

    # SIMPLE FLOW
    if not execution_plan[
        "requires_reasoning"
    ]:

        query_started_at = (
            time.perf_counter()
        )

        query_result = (
            service.ask_with_metadata(
                payload.question,
                row_limit=payload.row_limit,
            )
        )

        timings["query_ms"] = int(
            (
                time.perf_counter()
                - query_started_at
            ) * 1000
        )

        dataframe = query_result[
            "dataframe"
        ]

        rows = dataframe_to_rows(
            dataframe,
            limit=payload.row_limit,
        )

        summary_started_at = (
            time.perf_counter()
        )

        summary = summarize_query_result(
            llm=service.llm,
            question=payload.question,
            sql=query_result["sql"],
            rows=rows,
            max_tokens=service.settings.summary_max_tokens,
        )

        timings["summary_ms"] = int(
            (
                time.perf_counter()
                - summary_started_at
            ) * 1000
        )

        response = build_query_response(
            question=payload.question,
            sql=query_result["sql"],
            rows=rows,
            summary=summary,
            timings=timings,
            query_result=query_result,
            service=service,
            execution_ms=int(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000
            ),
        )

    # REASONING FLOW
    else:

        findings = []

        for task in execution_plan[
            "tasks"
        ]:

            task_result = (
                service.ask_with_metadata(
                    question=task[
                        "question"
                    ],
                    row_limit=payload.row_limit,
                    context={
                        "intent": execution_plan[
                            "intent"
                        ],
                        "agent": task[
                            "agent"
                        ],
                        "mart": task[
                            "mart"
                        ],
                    },
                )
            )

            findings.append(
                {
                    "agent": task[
                        "agent"
                    ],
                    "mart": task[
                        "mart"
                    ],
                    "sql": task_result[
                        "sql"
                    ],
                    "rows": dataframe_to_rows(
                        task_result[
                            "dataframe"
                        ],
                        limit=10,
                    ),
                }
            )

        summary = summarize_query_result(
            llm=service.llm,
            question=payload.question,
            sql="MULTI_STEP_REASONING",
            rows=findings,
            max_tokens=service.settings.summary_max_tokens,
        )

        response = {
            "question": payload.question,
            "summary": summary,
            "evidence": findings,
            "cache_hit": False,
            "execution_ms": int(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000
            ),
        }

    response_cache.set(
        question=payload.question,
        schema_version=service.schema_version,
        row_limit=payload.row_limit,
        payload=response,
        response_version=response_version,
    )

    return response