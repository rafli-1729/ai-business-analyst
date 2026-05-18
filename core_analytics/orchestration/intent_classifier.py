TREND_KEYWORDS = {
    "trend",
    "growth",
    "increase",
    "decrease",
    "monthly",
    "yearly",
    "seasonal",
    "why",
}

RANKING_KEYWORDS = {
    "top",
    "best",
    "highest",
    "lowest",
    "rank",
}

DIAGNOSTIC_KEYWORDS = {
    "why",
    "reason",
    "cause",
    "driver",
    "impact",
}


def classify_intent(question: str) -> str:

    normalized = question.lower()

    if any(
        keyword in normalized
        for keyword in DIAGNOSTIC_KEYWORDS
    ):
        return "diagnostic"

    if any(
        keyword in normalized
        for keyword in TREND_KEYWORDS
    ):
        return "trend"

    if any(
        keyword in normalized
        for keyword in RANKING_KEYWORDS
    ):
        return "ranking"

    return "general"