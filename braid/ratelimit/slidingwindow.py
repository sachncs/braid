"""Sliding-window rate limiter."""

from __future__ import annotations

import time
from collections import deque
from typing import Any

from braid.core.registry import registry


@registry.register(category="ratelimit", name="slidingwindow")
class slidingwindow:
    """Sliding-window rate limiter."""

    name: str = "slidingwindow"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency", "async"})

    def __init__(self, windowseconds: float = 60.0, maxcalls: int = 1000) -> None:
        self.windowseconds = windowseconds
        self.maxcalls = maxcalls
        self._calls: dict[str, deque[float]] = {}

    def allow(self, key: str = "default", cost: float = 1.0) -> bool:
        """Return True if the request fits in the window."""
        now = time.monotonic()
        if key not in self._calls:
            self._calls[key] = deque()
        dq = self._calls[key]
        cutoff = now - self.windowseconds
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) + cost > self.maxcalls:
            return False
        for _ in range(int(cost)):
            dq.append(now)
        return True

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
