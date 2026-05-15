AGENT_MAPPINGS = {
    "trend": "trend_agent",
    "ranking": "ranker_agent",
    "diagnostic": "diagnostic_agent",
}


def route_agent(intent: str) -> str:

    return AGENT_MAPPINGS.get(
        intent,
        "trend_agent",
    )