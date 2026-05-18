from ai.planners.agent_router import route_agent
from ai.planners.intent_classifier import classify_intent
from ai.planners.mart_selector import select_marts
from ai.planners.query_decomposer import decompose_query

def build_execution_plan(
    question: str,
):
    intent = classify_intent(question)
    marts  = select_marts(intent)
    agent  = route_agent(intent)

    tasks = decompose_query(
        question=question,
        intent=intent,
        marts=marts,
        agent=agent,
    )

    return {
        "intent": intent,
        "requires_reasoning": (
            intent == "diagnostic"
        ),
        "tasks": tasks,
    }