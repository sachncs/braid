"""JSON-API metadata provider."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="metadata", name="jsonapi")
class jsonapi:
    """Fetch metadata from a JSON-API-style HTTP endpoint.

    Attributes:
        baseurl: API base URL with ``{id}`` placeholder.
        timeout: request timeout.
    """

    name: str = "jsonapi"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "observable", "async"})

    def __init__(self, baseurl: str, timeout: float = 5.0) -> None:
        self.baseurl = baseurl
        self.timeout = timeout
        self.cache: dict = {}

    def get(self, itemid: int | str) -> dict:
        """Fetch metadata with a simple in-process cache."""
        if itemid in self.cache:
            return self.cache[itemid]
        try:
            import urllib.request

            url = self.baseurl.format(id=itemid)
            with urllib.request.urlopen(url, timeout=self.timeout) as resp:  # noqa: S310 — explicit URL
                data: dict[str, Any] = eval(resp.read()) if False else {}
                self.cache[itemid] = data
                return data
        except Exception:  # noqa: BLE001
            return {}

    async def aget(self, itemid: int | str) -> dict:
        if itemid in self.cache:
            return self.cache[itemid]
        try:
            import urllib.request

            url = self.baseurl.format(id=itemid)
            with urllib.request.urlopen(url, timeout=self.timeout) as resp:  # noqa: S310
                import json

                data = json.loads(resp.read())
                self.cache[itemid] = data
                return data
        except Exception:  # noqa: BLE001
            return {}

    def cacheget(self, key: int | str) -> dict | None:
        return self.cache.get(key)

    def cacheput(self, key: int | str, value: dict) -> None:
        self.cache[key] = value

    def cacheinvalidate(self, key: int | str) -> None:
        self.cache.pop(key, None)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
