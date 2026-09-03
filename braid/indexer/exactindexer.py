"""Exact (brute force) indexer."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="indexer", name="exactindexer")
class exactindexer:
    """Brute-force topk via sorted dot product."""

    name: str = "exactindexer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, embeddings: np.ndarray) -> None:
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.dim = self.embeddings.shape[1]
        self.numitems = self.embeddings.shape[0]

    def query(self, vector: np.ndarray, topk: int = 10) -> np.ndarray:
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
