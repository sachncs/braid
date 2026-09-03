"""Adaptive curriculum.

Adjusts difficulty based on running loss slope.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="curriculum", name="adaptivecurriculum")
class adaptivecurriculum:
    """Difficulty adapts to recent loss improvements."""

    name: str = "adaptivecurriculum"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, maxtries: int = 5, minlossdelta: float = 0.01) -> None:
        self.maxtries = maxtries
        self.minlossdelta = minlossdelta
        self._prevloss: float | None = None
        self._stagnation: int = 0
        self._difficulty: float = 0.0

    def difficulty(self, step: int) -> float:
        return self._difficulty

    def step(self, loss: float) -> float:
        """Update internal state and return new difficulty."""
        if self._prevloss is None:
            self._prevloss = loss
        else:
            delta = self._prevloss - loss
            if delta < self.minlossdelta:
                self._stagnation += 1
            else:
                self._stagnation = 0
                self._difficulty = min(1.0, self._difficulty + 0.1)
            if self._stagnation >= self.maxtries:
                self._difficulty = max(0.0, self._difficulty - 0.05)
                self._stagnation = 0
            self._prevloss = loss
        return self._difficulty

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
