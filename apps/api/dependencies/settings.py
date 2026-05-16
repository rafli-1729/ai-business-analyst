from functools import lru_cache

from infra.config.settings import get_settings
from ai.orchestrators.analytical_orchestrator import AnalyticalOrchestrator
from ai.caches.response_cache import ResponseCache


@lru_cache(maxsize=1)
def get_orchestrator() -> AnalyticalOrchestrator:
    """Get or create analytical orchestrator singleton."""
    return AnalyticalOrchestrator(get_settings())


@lru_cache(maxsize=1)
def get_response_cache() -> ResponseCache:
    """Get or create response cache singleton."""
    settings = get_settings()
    return ResponseCache(ttl_seconds=settings.response_cache_ttl_s)
