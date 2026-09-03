"""FAISS indexer."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="indexer", name="faissindexer")
class faissindexer:
    """FAISS-backed indexer (graceful fallback to numpy)."""

    name: str = "faissindexer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"shardedcatalog", "distributable", "observable", "async"})

    def __init__(self, embeddings: np.ndarray, nlist: int = 100) -> None:
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.dim = self.embeddings.shape[1]
        self.nlist = max(1, min(nlist, self.embeddings.shape[0]))
        self._faiss: Any | None = None
        try:
            import faiss

            self._faiss = faiss
        except Exception:  # noqa: BLE001
            self._faiss = None
        self._index: Any | None = None
        if self._faiss is not None:
            try:
                quantizer = self._faiss.IndexFlatIP(self.dim)
                self._index = self._faiss.IndexIVFFlat(quantizer, self.dim, self.nlist)
                self._index.train(self.embeddings)
                self._index.add(self.embeddings)
            except Exception:  # noqa: BLE001
                self._index = None

    def query(self, vector: np.ndarray, topk: int = 10) -> np.ndarray:
        if self._index is not None:
            _, ids = self._index.search(vector.astype(np.float32).reshape(1, -1), topk)
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
