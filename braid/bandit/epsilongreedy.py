"""Epsilon-greedy bandit."""

from __future__ import annotations

import random
from typing import Any

from braid.core.registry import registry


@registry.register(category="bandit", name="epsilongreedy")
class epsilongreedy:
    """Epsilon-greedy policy."""

    name: str = "epsilongreedy"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"banditarmed", "observable"})

    def __init__(self, n_arms: int, epsilon: float = 0.1, seed: int = 0) -> None:
        self.narms = n_arms
        self.epsilon = epsilon
        self.counts = [0] * n_arms
        self.values = [0.0] * n_arms
        self.rng = random.Random(seed)

    def select(self) -> int:
        """Pick an arm index."""
        if self.rng.random() < self.epsilon:
            return self.rng.randrange(self.narms)
        best = 0
        bestval = -1e9
        for i, v in enumerate(self.values):
            if v > bestval:
                bestval = v
                best = i
        return best

    def update(self, arm: int, reward: float) -> None:
        n = self.counts[arm] + 1
        value = self.values[arm]
        self.values[arm] = ((n - 1) * value + reward) / n
        self.counts[arm] = n

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
