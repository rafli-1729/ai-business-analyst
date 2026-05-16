import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str
    database_url: str
    llm_model: str
    debug: bool = False
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_timeout_s: int = 30
    llm_max_retries: int = 2
    llm_temperature: float = 0.0
    llm_max_tokens: int = 600
    summary_max_tokens: int = 450
    sql_cache_ttl_s: int = 3600
    response_cache_ttl_s: int = 900
    max_question_chars: int = 800


def get_settings() -> Settings:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    db_url = os.getenv("LLM_DB_URL", "").strip()

    if not api_key:
        raise ValueError("Missing OPENROUTER_API_KEY")
    if not db_url:
        raise ValueError("Missing LLM_DB_URL")

    return Settings(
        openrouter_api_key=api_key,
        database_url=db_url,
        debug=_read_bool("DEBUG", default=False),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        llm_model=os.getenv("LLM_MODEL", ""),
        llm_timeout_s=int(os.getenv("LLM_TIMEOUT_S", "30")),
        llm_max_retries=int(os.getenv("LLM_MAX_RETRIES", "2")),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
        llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "600")),
        summary_max_tokens=int(os.getenv("SUMMARY_MAX_TOKENS", "450")),
        sql_cache_ttl_s=int(os.getenv("SQL_CACHE_TTL_S", "3600")),
        response_cache_ttl_s=int(os.getenv("RESPONSE_CACHE_TTL_S", "900")),
        max_question_chars=int(os.getenv("MAX_QUESTION_CHARS", "800")),
    )


def _read_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}
