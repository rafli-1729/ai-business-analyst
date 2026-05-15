class RankerAgent:

    def prepare_context(
        self,
        question: str,
        mart: str,
    ):

        return {
            "intent": "ranking_analysis",
            "mart": mart,
            "focus": [
                "top_n",
                "comparisons",
                "aggregations",
            ],
        }