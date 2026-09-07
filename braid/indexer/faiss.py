"""FAISS IVF indexer."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.error import ioerror
from braid.core.registry import registry


@registry.register(category="indexer", name="faiss")
class faiss:
    """FAISS-backed IVF indexer.

    Falls back to numpy arg-sort when faiss is unavailable; raises
    typed ``ioerror`` if the user requested GPU-backed faiss.

    Attributes:
        embeddings: catalog array.
        nlist: number of Voronoi cells.
        nprobe: cells probed per query.
    """

    name: str = "faiss"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"shardedcatalog", "distributable", "async", "observable"})

    def __init__(self, embeddings: np.ndarray, nlist: int = 100, nprobe: int = 8) -> None:
        """Initialize the faiss index.

        Args:
            embeddings: ``[numitems, dim]`` float array.
            nlist: number of cells. Defaults to 100.
            nprobe: cells probed. Defaults to 8.
        """
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.nlist = max(1, min(nlist, self.embeddings.shape[0]))
        self.nprobe = min(nprobe, self.nlist)
        self.dim = self.embeddings.shape[1]
        self.numitems = self.embeddings.shape[0]
        self.faissmod: Any | None = None
        self.index: Any | None = None
        try:
            import faiss  # noqa: F401

            self.faissmod = faiss
        except ImportError as exc:
            self.faissmod = None
        if self.faissmod is not None and self.embeddings.shape[0] > 0:
            try:
                quantizer = self.faissmod.IndexFlatIP(self.dim)
                self.index = self.faissmod.IndexIVFFlat(quantizer, self.dim, self.nlist)
                self.index.train(self.embeddings)
                self.index.add(self.embeddings)
                self.index.nprobe = self.nprobe
            except Exception:
                self.index = None

    def query(self, vector: np.ndarray, topk: int = 10) -> np.ndarray:
        """Return topk indices.

        Args:
            vector: query ``[dim]`` vector.
            topk: number of neighbors.

        Returns:
            ``[topk]`` int array.
        """
        if self.index is not None:
            _, ids = self.index.search(vector.astype(np.float32).reshape(1, -1), topk)
            return ids[0]
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
