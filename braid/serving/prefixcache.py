"""Shared KV-cache prefix utilities."""

from __future__ import annotations

from typing import Any


class prefixcache:
    """In-process prefix cache for shared system prompts."""

    def __init__(self) -> None:
        self.cache: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        return self.cache.get(key)

    def put(self, key: str, value: Any) -> None:
        self.cache[key] = value

    def invalidate(self, key: str) -> None:
        self.cache.pop(key, None)
