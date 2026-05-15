import time
from openai import OpenAI

from infra.observability.logger import log_event


class LlmClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout_s: int = 30, max_retries: int = 2, temperature: float = 0, max_tokens: int | None = None):
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout_s)
        self.model = model
        self.max_retries = max_retries
        self.temperature = temperature
        self.max_tokens = max_tokens

    def invoke(self, prompt: str, request_id: str = "summary", max_tokens: int | None = None) -> str:
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                request = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                }
                token_limit = max_tokens if max_tokens is not None else self.max_tokens
                if token_limit:
                    request["max_tokens"] = token_limit

                response = self.client.chat.completions.create(
                    **request
                )

                content = response.choices[0].message.content or ""

                usage = getattr(response, "usage", None)
                prompt_tokens = getattr(usage, "prompt_tokens", None) if usage else None
                completion_tokens = getattr(usage, "completion_tokens", None) if usage else None

                log_event(
                    "llm_invoke_success",
                    request_id=request_id,
                    attempt=attempt,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                )

                return content.strip()

            except Exception as e:
                last_error = e

                log_event(
                    "llm_invoke_retry",
                    request_id=request_id,
                    attempt=attempt,
                    error=str(e),
                )

                time.sleep(min(2 ** attempt, 8))

        raise RuntimeError(f"LLM invoke failed after retries: {last_error}")


    def generate_sql(self, prompt: str, request_id: str) -> str:
        return self.invoke(prompt, request_id=request_id)
