"""Adaptive difficulty curriculum."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="curriculum", name="adaptive")
class adaptive:
    """Difficulty adapts to recent loss improvements.

    Difficulty grows on loss improvement, decays on stagnation.

    Attributes:
        maxtries: stagnation count before decay kicks in.
        minlossdelta: minimum loss change considered improvement.
        difficulty: current difficulty in ``[0, 1]``.
    """

    name: str = "adaptive"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, maxtries: int = 5, minlossdelta: float = 0.01) -> None:
        if maxtries <= 0:
            raise ValueError("maxtries must be > 0")
        if minlossdelta < 0:
            raise ValueError("minlossdelta must be >= 0")
        self.maxtries = maxtries
        self.minlossdelta = minlossdelta
        self._prevloss: float | None = None
        self._stagnation: int = 0
        self._difficulty: float = 0.0

    def difficulty(self, step: int) -> float:
        """Return current difficulty in [0, 1]."""
        return self._difficulty

    def step(self, loss: float) -> float:
        """Update internal state given a new loss and return new difficulty.

        Args:
            loss: current batch loss.

        Returns:
            Updated difficulty in ``[0, 1]``.
        """
        if self._prevloss is None:
            self._prevloss = loss
            return self._difficulty
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
        return {"metrics": [{"name": "braid.curriculum.adaptive.difficulty", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
