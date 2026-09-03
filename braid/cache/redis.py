"""Redis cache backend."""

from __future__ import annotations

import json
from typing import Any

from braid.core.registry import registry


@registry.register(category="cache", name="redis")
class redis:
    """Redis-backed cache."""

    name: str = "redis"
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
            import redis as redisclient

            self._client = redisclient.Redis.from_url(self.url)
        except Exception:  # noqa: BLE001
            self._client = None

    def get(self, key: Any) -> Any | None:
        if self._client is None:
            return None
        try:
            raw = self._client.get(self.prefix + str(key))
            return json.loads(raw) if raw else None
        except Exception:  # noqa: BLE001
            return None

    def put(self, key: Any, value: Any) -> None:
        if self._client is None:
            return
        try:
            self._client.setex(self.prefix + str(key), self.ttl, json.dumps(value, default=str))
        except Exception:  # noqa: BLE001
            return

    def invalidate(self, key: Any) -> None:
        if self._client is None:
            return
        try:
            self._client.delete(self.prefix + str(key))
        except Exception:  # noqa: BLE001
            return

    async def aget(self, key: Any) -> Any | None:
        return self.get(key)

    async def aput(self, key: Any, value: Any) -> None:
        self.put(key, value)

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.cache.redis.latency", "type": "histogram"}]}

    def metrics(self) -> list[Any]:
        return []
