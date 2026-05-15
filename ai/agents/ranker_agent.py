class RankerAgent:

    def build_prompt(
        self,
        question: str,
        mart: str,
    ) -> str:

        return f"""
            You are a ranking and aggregation analyst.

            Focus on:
            - top N
            - rankings
            - grouped comparisons

            Generate a PostgreSQL query using:
            {mart}

            Question:
            {question}

            Only return PostgreSQL SQL.
        """