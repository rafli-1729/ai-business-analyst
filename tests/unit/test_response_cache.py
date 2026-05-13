from services.response_cache import ResponseCache


def test_response_cache_uses_response_version_in_key():
    cache = ResponseCache(ttl_seconds=60)
    cache.set("top revenue", "schema-v1", 100, {"summary": "old"}, response_version="summary-v1")

    assert cache.get("top revenue", "schema-v1", 100, response_version="summary-v2") is None
    assert cache.get("top revenue", "schema-v1", 100, response_version="summary-v1") == {"summary": "old"}
