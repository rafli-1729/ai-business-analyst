import time
from openai import OpenAI

from services.observability import log_event


class LlmClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout_s: int = 30, max_retries: int = 2, temperature: float = 0):
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout_s)
        self.model = model
        self.max_retries = max_retries
        self.temperature = temperature

    def generate_sql(self, prompt: str, request_id: str) -> str:
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}],
                )
                sql = response.choices[0].message.content or ""
                usage = getattr(response, "usage", None)
                prompt_tokens = getattr(usage, "prompt_tokens", None) if usage else None
                completion_tokens = getattr(usage, "completion_tokens", None) if usage else None
                log_event("llm_call_success", request_id=request_id, attempt=attempt, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
                return sql.strip()
            except Exception as e:
                last_error = e
                log_event("llm_call_retry", request_id=request_id, attempt=attempt, error=str(e))
                time.sleep(min(2 ** attempt, 8))
        raise RuntimeError(f"LLM call failed after retries: {last_error}")
