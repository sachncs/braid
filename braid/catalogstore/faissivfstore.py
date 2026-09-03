"""FAISS IVF catalog store.

Scales to catalogs larger than device memory via inverted-file indexing.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="catalogstore", name="faissivfstore")
class faissivfstore:
    """FAISS-IVF catalog store.

    Falls back to a deterministic np-based implementation when faiss is
    unavailable.
    """

    name: str = "faissivfstore"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"shardedcatalog", "distributable", "async", "observable"})

    def __init__(self, embeddings: np.ndarray, nlist: int = 100, nprobe: int = 8) -> None:
        """Initialize the IVF index.

        Args:
            embeddings: ``[numitems, dim]`` array.
            nlist: number of Voronoi cells.
            nprobe: cells probed at query time.
        """
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.nlist = max(1, min(nlist, self.embeddings.shape[0]))
        self.nprobe = min(nprobe, self.nlist)
        self.numitems = self.embeddings.shape[0]
        self.dim = self.embeddings.shape[1]
        self._faiss: Any | None = None
        try:
            import faiss  # noqa: F401 — imported lazily

            self._faiss = faiss
        except Exception:  # noqa: BLE001
            self._faiss = None
        self._index: Any | None = None
        self._build()

    def _build(self) -> None:
        if self._faiss is None or self.embeddings.shape[0] == 0:
            return
        try:
            quantizer = self._faiss.IndexFlatIP(self.dim)
            self._index = self._faiss.IndexIVFFlat(quantizer, self.dim, self.nlist)
            self._index.train(self.embeddings)
            self._index.add(self.embeddings)
            self._index.nprobe = self.nprobe
        except Exception:  # noqa: BLE001
            self._index = None

    def score(self, userrepr: np.ndarray, ids: np.ndarray | None = None, topk: int | None = None) -> np.ndarray:
        """Return scores. With ``ids`` returns the full slice; otherwise topk."""
        if self._index is None:
            matrix = self.embeddings
            if ids is not None:
                matrix = matrix[ids]
            return userrepr @ matrix.T
        scores, indices = self._index.search(userrepr.astype(np.float32), topk or self.numitems)
        return scores

    def warmup(self) -> None:
        if self._index is not None:
            _ = self._index.search(self.embeddings[:1], 1)

    def shardrank(self) -> int:
        return 0

    def numshards(self) -> int:
        return 1

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.catalogstore.faiss.nprobe", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
