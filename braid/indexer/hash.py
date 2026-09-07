"""Hash indexer (LSH — locality-sensitive hashing)."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="indexer", name="hash")
class hash:
    """Locality-sensitive hash indexer for fast approximate lookup.

    Attributes:
        embeddings: ``[numitems, dim]`` array.
        numitems: number of items.
        dim: embedding dimension.
        planes: random LSH projection planes, ``[nbits, dim]``.
        codes: per-item binary LSH codes, ``[numitems, nbits]``.
    """

    name: str = "hash"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"shardedcatalog", "distributable", "observable"})

    def __init__(self, embeddings: np.ndarray, nbits: int = 128, seed: int = 0) -> None:
        """Initialize the LSH index.

        Args:
            embeddings: ``[numitems, dim]`` catalog embeddings.
            nbits: number of random hyperplanes. Defaults to 128.
            seed: RNG seed. Defaults to 0.
        """
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.dim = self.embeddings.shape[1]
        rng = np.random.default_rng(seed)
        self.planes = rng.standard_normal((nbits, self.dim), dtype=np.float32)
        self.codes = (self.embeddings @ self.planes.T > 0).astype(np.uint8)
        self.numitems = self.embeddings.shape[0]

    def query(self, vector: np.ndarray, topk: int = 10) -> np.ndarray:
        """Return topk indices by Hamming distance.

        Args:
            vector: query ``[dim]`` vector.
            topk: number of nearest neighbors.

        Returns:
            ``[topk]`` int array of item indices.
        """
        code = (vector @ self.planes.T > 0).astype(np.uint8)
        hamming = np.sum(self.codes != code[None, :], axis=1)
        return np.argsort(hamming)[:topk]

    def shardrank(self) -> int:
        return 0

    def numshards(self) -> int:
        return 1

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
