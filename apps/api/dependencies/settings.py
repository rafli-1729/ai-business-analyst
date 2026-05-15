from functools import lru_cache

from infra.config.settings import get_settings
from ai.services.query_service import QueryService
from ai.services.response_cache import ResponseCache


@lru_cache(maxsize=1)
def get_query_service() -> QueryService:
    return QueryService(get_settings())


@lru_cache(maxsize=1)
def get_response_cache() -> ResponseCache:
    settings = get_settings()
    return ResponseCache(ttl_seconds=settings.response_cache_ttl_s)
