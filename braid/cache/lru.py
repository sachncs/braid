"""In-memory LRU cache."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

from braid.core.registry import registry


@registry.register(category="cache", name="lru")
class lru:
    """Thread-unsafe in-process LRU cache."""

    name: str = "lru"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "observable", "lowlatency"})

    def __init__(self, maxentries: int = 10000) -> None:
        if maxentries <= 0:
            raise ValueError("maxentries must be > 0")
        self.maxentries = maxentries
        self.data: "OrderedDict[Any, Any]" = OrderedDict()

    def get(self, key: Any) -> Any | None:
        """Return cached value or None; update recency."""
        if key in self.data:
            self.data.move_to_end(key)
            return self.data[key]
        return None

    def put(self, key: Any, value: Any) -> None:
        """Insert; evict LRU if over capacity."""
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        while len(self.data) > self.maxentries:
            self.data.popitem(last=False)

    def invalidate(self, key: Any) -> None:
        self.data.pop(key, None)

    def size(self) -> int:
        return len(self.data)

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.cache.lru.hits", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
