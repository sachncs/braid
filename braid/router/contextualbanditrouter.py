"""Contextual-bandit router (LinUCB)."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="router", name="contextualbanditrouter")
class contextualbanditrouter:
    """LinUCB contextual bandit router.

    Attributes:
        arms: list of arm names.
        dim: feature dimension.
        alpha: exploration coefficient.
    """

    name: str = "contextualbanditrouter"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency", "async", "banditarmed"})

    def __init__(self, arms: list[str] | None = None, dim: int = 16, alpha: float = 1.0) -> None:
        self.arms = arms or ["control", "treatment"]
        self.dim = dim
        self.alpha = alpha
        self.A: dict[str, np.ndarray] = {a: np.eye(dim) for a in self.arms}
        self.b: dict[str, np.ndarray] = {a: np.zeros(dim) for a in self.arms}

    def route(self, key: str | None = None, context: np.ndarray | None = None) -> str:
        """Pick an arm via LinUCB scores."""
        if context is None:
            context = np.zeros(self.dim)
        bestarm = self.arms[0]
        bestscore = -1e9
        for a in self.arms:
            Ainv = np.linalg.inv(self.A[a])
            theta = Ainv @ self.b[a]
            ucb = float(theta @ context + self.alpha * np.sqrt(context @ Ainv @ context))
            if ucb > bestscore:
                bestscore = ucb
                bestarm = a
        return bestarm

    def update(self, arm: str, context: np.ndarray, reward: float) -> None:
        """Update the bandit with a (context, reward) observation."""
        self.A[arm] += np.outer(context, context)
        self.b[arm] += reward * context

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
