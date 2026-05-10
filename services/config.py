import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str
    database_url: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "inclusionai/ring-2.6-1t:free"
    llm_timeout_s: int = 30
    llm_max_retries: int = 2
    llm_temperature: float = 0.0
    sql_cache_ttl_s: int = 3600
    max_question_chars: int = 800


def get_settings() -> Settings:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    db_url = os.getenv("DATABASE_URL", "").strip()

    if not api_key:
        raise ValueError("Missing OPENROUTER_API_KEY")
    if not db_url:
        raise ValueError("Missing DATABASE_URL")

    return Settings(
        openrouter_api_key=api_key,
        database_url=db_url,
        llm_model=os.getenv("LLM_MODEL", "inclusionai/ring-2.6-1t:free"),
        llm_timeout_s=int(os.getenv("LLM_TIMEOUT_S", "30")),
        llm_max_retries=int(os.getenv("LLM_MAX_RETRIES", "2")),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
        sql_cache_ttl_s=int(os.getenv("SQL_CACHE_TTL_S", "3600")),
        max_question_chars=int(os.getenv("MAX_QUESTION_CHARS", "800")),
    )
