"""Memcached cache backend."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="cache", name="memcached")
class memcached:
    """Memcached-backed cache."""

    name: str = "memcached"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "async", "observable", "distributable"})

    def __init__(self, url: str, ttl: int = 3600, prefix: str = "braid:") -> None:
        self.url = url
        self.ttl = ttl
        self.prefix = prefix
        self._client: Any | None = None
        self._connect()

    def _connect(self) -> None:
        try:
            from pymemcache.client.base import Client

            host, _, port = self.url.partition(":")
            self._client = Client((host, int(port or 11211)))
        except Exception:  # noqa: BLE001
            self._client = None

    def get(self, key: Any) -> Any | None:
        if self._client is None:
            return None
        try:
            return self._client.get(self.prefix + str(key))
        except Exception:  # noqa: BLE001
            return None

    def put(self, key: Any, value: Any) -> None:
        if self._client is None:
            return
        try:
            self._client.set(self.prefix + str(key), value, expire=self.ttl)
        except Exception:  # noqa: BLE001
            return

    def invalidate(self, key: Any) -> None:
        self.put(self.prefix + str(key) + ":del", "1")

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
