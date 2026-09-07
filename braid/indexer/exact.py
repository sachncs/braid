"""Exact (brute-force) indexer."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="indexer", name="exact")
class exact:
    """Brute-force topk via sorted inner product.

    Attributes:
        embeddings: ``[numitems, dim]`` array.
        dim, numitems: derived.
    """

    name: str = "exact"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, embeddings: np.ndarray) -> None:
        """Initialize the exact index.

        Args:
            embeddings: ``[numitems, dim]`` float32 catalog embeddings.
        """
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.dim = self.embeddings.shape[1]
        self.numitems = self.embeddings.shape[0]

    def query(self, vector: np.ndarray, topk: int = 10) -> np.ndarray:
        """Return topk indices by inner product (descending).

        Args:
            vector: query ``[dim]`` vector.
            topk: number of nearest neighbors.

        Returns:
            ``[topk]`` int array of item indices.
        """
        scores = self.embeddings @ vector
        return np.argsort(-scores)[:topk]

    def shardrank(self) -> int:
        return 0

    def numshards(self) -> int:
        return 1

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
