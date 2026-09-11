"""In-memory matmul catalog store.

Scores a single user representation vector against a catalog embedding
matrix in one BLAS call. The default scoring backend for catalogs <= 1M.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="catalogstore", name="matmulinmem")
class matmulinmem:
    """In-memory matmul catalog store."""

    name: str = "matmulinmem"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset(
        {"gpu", "fusedkernel", "distributable", "shardedcatalog", "observable", "cachable", "async"}
    )

    def __init__(self, embeddings: np.ndarray | list[list[float]]) -> None:
        """Initialize with catalog embeddings.

        Args:
            embeddings: ``[numitems, dim]`` array.
        """
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        if self.embeddings.ndim != 2:
            raise ValueError("embeddings must be 2-dimensional")
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-8
        self.embeddings = self.embeddings / norms
        self.numitems = self.embeddings.shape[0]
        self.dim = self.embeddings.shape[1]

    def score(self, userrepr: np.ndarray, ids: np.ndarray | None = None) -> np.ndarray:
        """Score ``userrepr`` against all or a subset of items.

        Args:
            userrepr: ``[batch, dim]`` user representations.
            ids: optional subset of item ids.

        Returns:
            ``[batch, numitems|len(ids)]`` similarity scores.
        """
        matrix = self.embeddings if ids is None else self.embeddings[ids]
        return userrepr @ matrix.T

    def warmup(self) -> None:
        """Pre-touch memory."""
        _ = self.embeddings @ self.embeddings[0]

    async def warmupasync(self) -> None:
        self.warmup()

    def shardrank(self) -> int:
        return 0

    def numshards(self) -> int:
        return 1

    def cacheget(self, key: int) -> np.ndarray | None:
        return self.embeddings[key] if 0 <= key < self.numitems else None

    def cacheput(self, key: int, value: np.ndarray) -> None:
        if 0 <= key < self.numitems:
            self.embeddings[key] = value

    def cacheinvalidate(self, key: int) -> None:
        return None

    def observability(self) -> dict[str, Any]:
        return {
            "metrics": [
                {
                    "name": "braid.catalogstore.score.duration",
                    "type": "histogram",
                    "labels": ("numitems",),
                },
                {
                    "name": "braid.catalogstore.score.calls",
                    "type": "counter",
                    "labels": ("numitems",),
                },
            ]
        }

    def metrics(self) -> list[Any]:
        return []
