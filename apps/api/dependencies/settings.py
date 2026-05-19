from functools import lru_cache
from infra.config.settings import get_settings
from core_analytics.analytics.engine import AnalyticsEngine
from core_analytics.analytics.cache import ResponseCache

@lru_cache(maxsize=1)
def get_orchestrator() -> AnalyticsEngine:
    """Get or create analytics engine singleton."""
    return AnalyticsEngine()

@lru_cache(maxsize=1)
def get_response_cache() -> ResponseCache:
    """Get or create response cache singleton."""
    settings = get_settings()
    return ResponseCache(ttl_seconds=settings.response_cache_ttl_s)
