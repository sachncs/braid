"""Adaptive difficulty curriculum.

Difficulty grows on loss improvement, decays on stagnation. Uses
public attribute names exclusively (no leading underscores) — see
the class docstring for which fields are operational state vs.
contractual surface.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="curriculum", name="adaptive")
class adaptive:
    """Difficulty adapts to recent loss improvements.

    Operational state (set during ``step``):
        prevloss: last observed loss.
        stagnation: consecutive count of stagnation rounds.
        difficulty: current difficulty in ``[0, 1]``.

    Attributes:
        maxtries: stagnation count before decay kicks in.
        minlossdelta: minimum loss change considered improvement.
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
        self.prevloss: float | None = None
        self.stagnation: int = 0
        self.difficulty: float = 0.0

    def getdifficulty(self, step: int) -> float:
        """Return current difficulty in [0, 1]."""
        return self.difficulty

    def step(self, loss: float) -> float:
        """Update internal state given a new loss and return new difficulty.

        Args:
            loss: current batch loss.

        Returns:
            Updated difficulty in ``[0, 1]``.
        """
        if self.prevloss is None:
            self.prevloss = loss
            return self.difficulty
        delta = self.prevloss - loss
        if delta < self.minlossdelta:
            self.stagnation += 1
        else:
            self.stagnation = 0
            self.difficulty = min(1.0, self.difficulty + 0.1)
        if self.stagnation >= self.maxtries:
            self.difficulty = max(0.0, self.difficulty - 0.05)
            self.stagnation = 0
        self.prevloss = loss
        return self.difficulty

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.curriculum.adaptive.difficulty", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
