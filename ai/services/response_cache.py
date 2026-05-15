import hashlib
import time
from typing import Any


class ResponseCache:
    def __init__(self, ttl_seconds: int = 900):
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[dict[str, Any], float]] = {}

    @staticmethod
    def _key(question: str, schema_version: str, row_limit: int, response_version: str = "v1") -> str:
        normalized_question = " ".join(question.lower().split())
        raw = f"{schema_version}|{response_version}|{row_limit}|{normalized_question}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def get(
        self,
        question: str,
        schema_version: str,
        row_limit: int,
        response_version: str = "v1",
    ) -> dict[str, Any] | None:
        key = self._key(question, schema_version, row_limit, response_version)
        value = self._store.get(key)
        if not value:
            return None

        payload, expires_at = value
        if time.time() > expires_at:
            self._store.pop(key, None)
            return None

        return dict(payload)

    def set(
        self,
        question: str,
        schema_version: str,
        row_limit: int,
        payload: dict[str, Any],
        response_version: str = "v1",
    ) -> None:
        key = self._key(question, schema_version, row_limit, response_version)
        self._store[key] = (dict(payload), time.time() + self.ttl_seconds)
