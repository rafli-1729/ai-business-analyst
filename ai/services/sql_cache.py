import hashlib
import time
from typing import Optional


class SqlCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self._store = {}

    @staticmethod
    def _key(question: str, schema_version: str) -> str:
        raw = f"{schema_version}|{question}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def get(self, question: str, schema_version: str) -> Optional[str]:
        key = self._key(question, schema_version)
        value = self._store.get(key)
        if not value:
            return None
        sql, expires_at = value
        if time.time() > expires_at:
            self._store.pop(key, None)
            return None
        return sql

    def set(self, question: str, schema_version: str, sql: str) -> None:
        key = self._key(question, schema_version)
        self._store[key] = (sql, time.time() + self.ttl_seconds)
