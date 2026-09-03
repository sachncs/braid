"""RQ-VAE catalog store proxy."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="rqvae", name="catalogstore")
class catalogstore:
    """Catalog store backed by RQ-VAE semantic IDs."""

    name: str = "catalogstore"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable", "speculative"})

    def __init__(self, codebook: np.ndarray, itemids: list[list[int]]) -> None:
        self.codebook = np.asarray(codebook, dtype=np.float32)
        self.itemids = itemids
        self.numitems = len(itemids)

    def score(self, userrepr: np.ndarray, ids: np.ndarray | None = None) -> np.ndarray:
        """Match user representation against semantic IDs."""
        batch = userrepr.shape[0]
        codes = self.codebook @ userrepr.T  # [codesize, batch]
        top = codes.argmax(axis=0)  # [batch]
        if ids is None:
            ids = np.arange(self.numitems)
        out = np.zeros((batch, len(ids)), dtype=np.float32)
        for j, iid in enumerate(ids.tolist()):
            seq = self.itemids[iid]
            if seq and seq[0] == int(top[0]):
                out[:, j] = 1.0
        return out

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
