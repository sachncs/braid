"""Token-bucket rate limiter."""

from __future__ import annotations

import time
from typing import Any

from braid.core.registry import registry


@registry.register(category="ratelimit", name="tokenbucket")
class tokenbucket:
    """Token-bucket rate limiter."""

    name: str = "tokenbucket"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency", "async"})

    def __init__(self, rate: float = 1000.0, capacity: float = 5000.0) -> None:
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last = time.monotonic()

    def allow(self, key: str = "default", cost: float = 1.0) -> bool:
        """Return True if the request is allowed."""
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

    def reset(self) -> None:
        self.tokens = self.capacity
        self.last = time.monotonic()

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.ratelimit.denied", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
