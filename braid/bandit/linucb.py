"""LinUCB contextual bandit."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="bandit", name="linucb")
class linucb:
    """LinUCB policy."""

    name: str = "linucb"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"banditarmed", "observable"})

    def __init__(self, n_arms: int, dim: int, alpha: float = 1.0) -> None:
        self.narms = n_arms
        self.dim = dim
        self.alpha = alpha
        self.A = [np.eye(dim) for _ in range(n_arms)]
        self.b = [np.zeros(dim) for _ in range(n_arms)]

    def select(self, context: np.ndarray) -> int:
        """Pick arm via UCB score."""
        scores = []
        for i in range(self.narms):
            Ainv = np.linalg.inv(self.A[i])
            theta = Ainv @ self.b[i]
            ucb = float(theta @ context + self.alpha * np.sqrt(max(0.0, context @ Ainv @ context)))
            scores.append(ucb)
        return int(np.argmax(scores))

    def update(self, arm: int, context: np.ndarray, reward: float) -> None:
        self.A[arm] += np.outer(context, context)
        self.b[arm] += reward * context

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
