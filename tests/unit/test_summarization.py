from core_analytics.analytics.summarization import remove_markdown_tables, summarize_query_result


class FakeLlm:
    def __init__(self, response: str):
        self.response = response
        self.prompt = ""

    def invoke(self, prompt: str, request_id: str, max_tokens: int | None = None) -> str:
        self.prompt = prompt
        return self.response


def test_summary_prompt_includes_no_table_instruction():
    llm = FakeLlm("Revenue is highest in health.")

    summarize_query_result(
        llm=llm,
        question="top revenue category",
        sql="select 1",
        rows=[{"category": "health", "revenue": 100}],
    )

    assert "Do not output markdown tables" in llm.prompt


def test_remove_markdown_tables_drops_pipe_table():
    content = """
Top categories:

| category | revenue |
| --- | ---: |
| health | 100 |

Health leads the ranking.
""".strip()

    assert remove_markdown_tables(content) == "Top categories:\n\nHealth leads the ranking."
