import hashlib
import json
import time

from typing import Any


class ResponseCache:

    def __init__(
        self,
        ttl_seconds: int = 900,
    ):

        self.ttl_seconds = ttl_seconds

        self._store: dict[
            str,
            tuple[
                dict[str, Any],
                float,
            ],
        ] = {}

    @staticmethod
    def _normalize_question(
        question: str,
    ) -> str:

        return " ".join(
            question.lower().split()
        )

    @staticmethod
    def _normalize_context(
        context: dict | None,
    ) -> str:

        if not context:
            return "no_context"

        return json.dumps(
            context,
            sort_keys=True,
        )

    @classmethod
    def _key(
        cls,
        question: str,
        schema_version: str,
        row_limit: int,
        response_version: str = "v1",
        context: dict | None = None,
    ) -> str:

        normalized_question = (
            cls._normalize_question(
                question
            )
        )

        normalized_context = (
            cls._normalize_context(
                context
            )
        )

        raw = (
            f"{schema_version}|"
            f"{response_version}|"
            f"{row_limit}|"
            f"{normalized_context}|"
            f"{normalized_question}"
        ).encode("utf-8")

        return hashlib.sha256(
            raw
        ).hexdigest()

    def get(
        self,
        question: str,
        schema_version: str,
        row_limit: int,
        response_version: str = "v1",
        context: dict | None = None,
    ) -> dict[str, Any] | None:

        key = self._key(
            question=question,
            schema_version=schema_version,
            row_limit=row_limit,
            response_version=response_version,
            context=context,
        )

        value = self._store.get(key)

        if not value:
            return None

        payload, expires_at = value

        if time.time() > expires_at:

            self._store.pop(
                key,
                None,
            )

            return None

        return dict(payload)

    def set(
        self,
        question: str,
        schema_version: str,
        row_limit: int,
        payload: dict[str, Any],
        response_version: str = "v1",
        context: dict | None = None,
    ) -> None:

        key = self._key(
            question=question,
            schema_version=schema_version,
            row_limit=row_limit,
            response_version=response_version,
            context=context,
        )

        self._store[key] = (
            dict(payload),
            time.time()
            + self.ttl_seconds,
        )

    def clear(self) -> None:

        self._store.clear()

    def stats(self) -> dict[str, Any]:

        return {
            "entries": len(
                self._store
            ),
            "ttl_seconds": (
                self.ttl_seconds
            ),
        }