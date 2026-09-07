"""Thompson sampling bandit."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="bandit", name="thompson")
class thompson:
    """Thompson sampling for Bernoulli rewards."""

    name: str = "thompson"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"banditarmed", "observable"})

    def __init__(self, n_arms: int, seed: int = 0) -> None:
        self.narms = n_arms
        self.alpha = [1.0] * n_arms
        self.beta = [1.0] * n_arms
        self.rng = np.random.default_rng(seed)

    def select(self) -> int:
        """Thompson-sample an arm."""
        samples = [self.rng.beta(self.alpha[i], self.beta[i]) for i in range(self.narms)]
        return int(np.argmax(samples))

    def update(self, arm: int, reward: float) -> None:
        if reward > 0:
            self.alpha[arm] += 1
        else:
            self.beta[arm] += 1

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
