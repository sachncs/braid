"""Popularity-aware miner.

Samples negatives inversely weighted by popularity (boosts cold items).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="miner", name="popularityawareminer")
class popularityawareminer:
    """Popularity-aware negative sampler."""

    name: str = "popularityawareminer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, popularity: np.ndarray, k: int = 64, alpha: float = 0.5, seed: int = 0) -> None:
        self.popularity = np.asarray(popularity, dtype=np.float64)
        if self.popularity.ndim != 1:
            raise ValueError("popularity must be 1D")
        self.k = k
        self.alpha = alpha
        self.rng = np.random.default_rng(seed)
        w = 1.0 / np.power(self.popularity + 1e-8, alpha)
        self.weights = w / w.sum()

    def mine(self, positives: Any, scoresfn: Any | None = None) -> Any:
        """Sample k negatives per positive inversely weighted by popularity."""
        n = positives.shape[0] if hasattr(positives, "shape") else len(positives)
        idx = self.rng.choice(len(self.weights), size=(n, self.k), p=self.weights)
        return idx

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
