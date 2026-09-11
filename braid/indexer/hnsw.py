"""HNSW (hierarchical navigable small world) indexer."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.error import ioerror
from braid.core.registry import registry


@registry.register(category="indexer", name="hnsw")
class hnsw:
    """HNSW approximate nearest-neighbor indexer backed by hnswlib.

    Attributes:
        embeddings: catalog array.
        m: HNSW M parameter.
        efconstruction, efsearch: HNSW search parameters.
    """

    name: str = "hnsw"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset(
        {"shardedcatalog", "distributable", "async", "observable"}
    )

    def __init__(
        self,
        embeddings: np.ndarray,
        m: int = 16,
        efconstruction: int = 200,
        efsearch: int = 50,
    ) -> None:
        """Initialize the HNSW index.

        Args:
            embeddings: ``[numitems, dim]`` array.
            m: M parameter. Defaults to 16.
            efconstruction: build-time ef. Defaults to 200.
            efsearch: query-time ef. Defaults to 50.
        """
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.dim = self.embeddings.shape[1]
        self.numitems = self.embeddings.shape[0]
        self.m = m
        self.efconstruction = efconstruction
        self.efsearch = efsearch
        self.index: Any | None = None
        try:
            import hnswlib

            self.index = hnswlib.Index(space="ip", dim=self.dim)
            self.index.init_index(
                max_elements=self.numitems,
                ef_construction=self.efconstruction,
                M=self.m,
            )
            self.index.add_items(self.embeddings)
            self.index.set_ef(self.efsearch)
        except ImportError:
            self.index = None
        except Exception as exc:  # noqa: BLE001
            raise ioerror(f"hnsw initialization failed: {exc}", retryable=False) from exc

    def query(self, vector: np.ndarray, topk: int = 10) -> np.ndarray:
        """Return topk indices; falls back to brute force if hnswlib unavailable."""
        if self.index is not None:
            ids, _ = self.index.knn_query(vector.reshape(1, -1), k=topk)
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
