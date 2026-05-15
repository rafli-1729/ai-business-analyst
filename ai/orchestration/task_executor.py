from ai.agents import AGENT_REGISTRY


class TaskExecutor:

    def __init__(
        self,
        query_service,
    ):
        self.query_service = query_service

    def execute_tasks(
        self,
        tasks: list[dict],
    ) -> list[dict]:

        findings = []

        for task in tasks:

            result = self.execute_task(
                task
            )

            findings.append(result)

        return findings

    def execute_task(
        self,
        task: dict,
    ) -> dict:

        agent = AGENT_REGISTRY[
            task["agent"]
        ]

        context = agent.prepare_context(
            question=task["question"],
            mart=task["mart"],
        )

        result = self.query_service.ask_with_metadata(
            question=task["question"],
            context=context,
        )

        return {
            "agent": task["agent"],
            "mart": task["mart"],
            "sql": result["sql"],
            "rows": result["dataframe"].to_dict(
                orient="records"
            ),
            "timings": result["timings"],
        }