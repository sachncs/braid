"""Popularity-aware negative miner.

Samples negatives inversely weighted by item popularity (boosts cold items).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="miner", name="popularity")
class popularity:
    """Popularity-aware negative sampler.

    Attributes:
        popularity: ``[numitems]`` array of item popularity counts.
        k: negatives per positive.
        alpha: power applied to popularity (higher favors cold items).
        rng: deterministic numpy RNG.
    """

    name: str = "popularity"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, popularity: np.ndarray, k: int = 64, alpha: float = 0.5, seed: int = 0) -> None:
        if k <= 0:
            raise ValueError("k must be > 0")
        pop = np.asarray(popularity, dtype=np.float64)
        if pop.ndim != 1:
            raise ValueError("popularity must be 1D")
        self.popularity = pop
        self.k = k
        self.alpha = alpha
        self.rng = np.random.default_rng(seed)
        weights = 1.0 / np.power(pop + 1e-8, alpha)
        self.weights = weights / weights.sum()

    def mine(self, positives: Any, scoresfn: Any | None = None) -> Any:
        """Sample k negatives per positive inversely weighted by popularity.

        Args:
            positives: ``[batch]`` positive item ids (length defines batch).
            scoresfn: unused.

        Returns:
            ``[batch, k]`` int64 numpy array of negative item ids.
        """
        n = positives.shape[0] if hasattr(positives, "shape") else len(positives)
        idx = self.rng.choice(len(self.weights), size=(n, self.k), p=self.weights)
        return idx

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
