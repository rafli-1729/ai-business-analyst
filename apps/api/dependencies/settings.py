from functools import lru_cache

from services.config import get_settings
from services.query_service import QueryService
from services.response_cache import ResponseCache


@lru_cache(maxsize=1)
def get_query_service() -> QueryService:
    return QueryService(get_settings())


@lru_cache(maxsize=1)
def get_response_cache() -> ResponseCache:
    settings = get_settings()
    return ResponseCache(ttl_seconds=settings.response_cache_ttl_s)
