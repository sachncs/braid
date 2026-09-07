"""Leaky-bucket rate limiter."""

from __future__ import annotations

import time
from typing import Any

from braid.core.registry import registry


@registry.register(category="ratelimit", name="leakybucket")
class leakybucket:
    """Leaky-bucket (drip) rate limiter."""

    name: str = "leakybucket"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency", "async"})

    def __init__(self, dripRate: float = 100.0, capacity: float = 1000.0) -> None:
        self.driprate = dripRate
        self.capacity = capacity
        self.level = 0.0
        self.last = time.monotonic()

    def allow(self, key: str = "default", cost: float = 1.0) -> bool:
        now = time.monotonic()
        self.level = max(0.0, self.level - (now - self.last) * self.driprate)
        self.last = now
        if self.level + cost <= self.capacity:
            self.level += cost
            return True
        return False

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
