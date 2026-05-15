class DiagnosticAgent:

    def prepare_context(
        self,
        question: str,
        mart: str,
    ):

        return {
            "intent": "diagnostic_analysis",
            "mart": mart,
            "focus": [
                "drivers",
                "root_causes",
                "supporting_evidence",
            ],
        }