"""FAISS IVF catalog store.

Scales to catalogs larger than device memory via inverted-file indexing.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="catalogstore", name="faissivfstore")
class faissivfstore:
    """FAISS-IVF catalog store.

    Requires ``faiss`` to be installed; raises :class:`requiresenvironment`
    otherwise rather than silently degrading to brute-force scoring.
    """

    name: str = "faissivfstore"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset(
        {"shardedcatalog", "distributable", "async", "observable"}
    )

    def __init__(self, embeddings: np.ndarray, nlist: int = 100, nprobe: int = 8) -> None:
        """Initialize the IVF index.

        Args:
            embeddings: ``[numitems, dim]`` array.
            nlist: number of Voronoi cells.
            nprobe: cells probed at query time.

        Raises:
            requiresenvironment: if faiss is not installed.
        """
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.nlist = max(1, min(nlist, self.embeddings.shape[0]))
        self.nprobe = min(nprobe, self.nlist)
        self.numitems = self.embeddings.shape[0]
        self.dim = self.embeddings.shape[1]
        try:
            import faiss

            self.faiss = faiss
        except ImportError as exc:
            raise requiresenvironment(
                "faiss required for catalogstore:faissivfstore",
                hint="pip install faiss-cpu",
            ) from exc
        self.index: Any | None = None
        self.build()

    def build(self) -> None:
        if self.faiss is None or self.embeddings.shape[0] == 0:
            return
        try:
            quantizer = self.faiss.IndexFlatIP(self.dim)
            self.index = self.faiss.IndexIVFFlat(quantizer, self.dim, self.nlist)
            self.index.train(self.embeddings)
            self.index.add(self.embeddings)
            self.index.nprobe = self.nprobe
        except Exception:  # noqa: BLE001
            self.index = None

    def score(
        self, userrepr: np.ndarray, ids: np.ndarray | None = None, topk: int | None = None
    ) -> np.ndarray:
        """Return scores. With ``ids`` returns the full slice; otherwise topk."""
        if self.index is None:
            matrix = self.embeddings
            if ids is not None:
                matrix = matrix[ids]
            return userrepr @ matrix.T
        scores, indices = self.index.search(userrepr.astype(np.float32), topk or self.numitems)
        return scores

    def warmup(self) -> None:
        if self.index is not None:
            _ = self.index.search(self.embeddings[:1], 1)

    def shardrank(self) -> int:
        return 0

    def numshards(self) -> int:
        return 1

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.catalogstore.faiss.nprobe", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
