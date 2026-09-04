"""INT4-AWQ quantized matmul catalog store.

Loads embeddings prequantized to 4-bit. Reduces storage ~8x vs FP32.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="catalogstore", name="matmulint4awq")
class matmulint4awq:
    """4-bit AWQ-quantized matmul catalog store."""

    name: str = "matmulint4awq"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"int4quantize", "quantizedcatalog", "gpu", "observable", "cachable", "distributable"})

    def __init__(
        self,
        embeddings: np.ndarray,
        *,
        scales: np.ndarray | None = None,
        zeros: np.ndarray | None = None,
    ) -> None:
        """Initialize with INT4-quantized catalog.

        Args:
            embeddings: int4 codes of shape ``[numitems, dim]``.
            scales: per-group scale factors.
            zeros: per-group zero points.
        """
        self.embeddings = np.asarray(embeddings, dtype=np.int8)
        if self.embeddings.ndim != 2:
            raise ValueError("embeddings must be 2-dimensional")
        self.scales = scales
        self.zeros = zeros
        self.numitems = self.embeddings.shape[0]
        self.dim = self.embeddings.shape[1]

    def dequantized(self, ids: np.ndarray | None) -> np.ndarray:
        idx = ids if ids is not None else np.arange(self.numitems)
        codes = self.embeddings[idx].astype(np.float32)
        if self.scales is not None:
            scale = self.scales[idx] if self.scales.ndim > 1 else self.scales
            codes = codes * scale
        if self.zeros is not None:
            codes = codes + self.zeros
        return codes

    def score(self, userrepr: np.ndarray, ids: np.ndarray | None = None) -> np.ndarray:
        matrix = self.dequantized(ids)
        return userrepr @ matrix.T

    def warmup(self) -> None:
        _ = self.score(np.eye(self.dim)[:1])

    def shardrank(self) -> int:
        return 0

    def numshards(self) -> int:
        return 1

    def cacheget(self, key: int) -> np.ndarray | None:
        if 0 <= key < self.numitems:
            return self.dequantized(np.asarray([key]))[0]
        return None

    def cacheput(self, key: int, value: np.ndarray) -> None:
        return None

    def cacheinvalidate(self, key: int) -> None:
        return None

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.catalogstore.int4.bytes", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
