"""Page-Hinkley sequential change-point detector."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="drift", name="pagehinkley")
class pagehinkley:
    """Page-Hinkley change-point detector."""

    name: str = "pagehinkley"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, delta: float = 0.005, threshold: float = 50.0, alpha: float = 1 - 1e-4) -> None:
        self.delta = delta
        self.threshold = threshold
        self.alpha = alpha
        self._mean = 0.0
        self._sum = 0.0
        self._count = 0

    def update(self, value: float) -> dict[str, Any]:
        """Update the detector with one value; report any change-point."""
        self._count += 1
        self._mean = self._mean + (value - self._mean) / self._count
        self._sum = self._sum + (value - self._mean - self.delta)
        score = self._sum - min(0.0, self._sum)
        return {"score": float(score), "drifted": abs(score) > self.threshold}

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.drift.pagehinkley.score", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
