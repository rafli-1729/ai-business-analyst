def decompose_query(
    question: str,
    intent: str,
    marts: list[str],
    agent: str,
):

    tasks = []

    for mart in marts:

        tasks.append(
            {
                "task_type": intent,
                "agent": agent,
                "mart": mart,
                "question": question,
            }
        )

    return tasks