from typing import Optional, Any

class ResponseCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self.data = {}

    def get(self, question: str, schema_version: str, row_limit: int, response_version: str = "v1") -> Optional[Any]:
        key = f"{question}:{schema_version}:{row_limit}:{response_version}"
        return self.data.get(key)

    def set(self, question: str, schema_version: str, row_limit: int, value: Any, response_version: str = "v1") -> None:
        key = f"{question}:{schema_version}:{row_limit}:{response_version}"
        self.data[key] = value
