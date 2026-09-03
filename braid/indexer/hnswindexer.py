"""HNSW (hierarchical navigable small world) indexer."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="indexer", name="hnswindexer")
class hnswindexer:
    """HNSW approximate nearest-neighbor indexer."""

    name: str = "hnswindexer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"shardedcatalog", "distributable", "async", "observable"})

    def __init__(self, embeddings: np.ndarray, m: int = 16, efconstruction: int = 200, efsearch: int = 50) -> None:
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.dim = self.embeddings.shape[1]
        self.m = m
        self.efconstruction = efconstruction
        self.efsearch = efsearch
        self._index: Any | None = None
        try:
            import hnswlib

            self._index = hnswlib.Index(space="ip", dim=self.dim)
            self._index.init_index(max_elements=self.embeddings.shape[0], ef_construction=self.efconstruction, M=self.m)
            self._index.add_items(self.embeddings)
            self._index.set_ef(self.efsearch)
        except Exception:  # noqa: BLE001
            self._index = None

    def query(self, vector: np.ndarray, topk: int = 10) -> np.ndarray:
        if self._index is not None:
            ids, _ = self._index.knn_query(vector.reshape(1, -1), k=topk)
            return ids[0]
        scores = self.embeddings @ vector
        return np.argsort(-scores)[:topk]

    def shardrank(self) -> int:
        return 0

    def numshards(self) -> int:
        return 1

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.indexer.hnsw.ef", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
