import os
import httpx
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = os.getenv("LLM_MODEL", "openai/gpt-3.5-turbo") # Default model

    def get_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            openai_api_key=self.api_key,
            openai_api_base=self.base_url,
            model_name=self.model,
            default_headers={"HTTP-Referer": "https://olist-agent-analyst.com"}
        )

    # Kept for backward compatibility during migration
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://olist-agent-analyst.com", # Required by OpenRouter
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        with httpx.Client() as client:
            response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
