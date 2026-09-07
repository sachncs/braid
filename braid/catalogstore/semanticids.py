"""Semantic-ID (RQ-VAE) catalog store.

Scores a user representation against items stored as discrete semantic
codes. Decode the user vector through ``quantizer.quantizer`` and match
items by prefix.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="catalogstore", name="semanticids")
class semanticids:
    """Catalog store backed by RQ-VAE semantic IDs.

    Attributes:
        codebook: ``[codebooksize, dim]`` array.
        itemids: list of semantic code sequences (one per item).
        numitems: number of items.
        dim: embedding dim of the codebook.
    """

    name: str = "semanticids"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable", "speculative"})

    def __init__(self, codebook: np.ndarray, itemids: list[list[int]]) -> None:
        """Initialize the semantic-ID store.

        Args:
            codebook: ``[codebooksize, dim]`` codebook array.
            itemids: list of per-item semantic code sequences.
        """
        self.codebook = np.asarray(codebook, dtype=np.float32)
        self.itemids = itemids
        self.numitems = len(itemids)
        self.dim = self.codebook.shape[1]

    def score(self, userrepr: np.ndarray, ids: np.ndarray | None = None) -> np.ndarray:
        """Match user representation against semantic-ID items.

        Args:
            userrepr: ``[batch, dim]`` user representation.
            ids: optional ``[k]`` subset of item ids; ``None`` scores full catalog.

        Returns:
            ``[batch, k|numitems]`` similarity scores.
        """
        batch = userrepr.shape[0]
        scores = self.codebook @ userrepr.T  # [codesize, batch]
        top = scores.argmax(axis=0)  # [batch]
        if ids is None:
            ids = np.arange(self.numitems)
        out = np.zeros((batch, len(ids)), dtype=np.float32)
        for j, iid in enumerate(ids.tolist()):
            seq = self.itemids[iid]
            if seq and seq[0] == int(top[0]):
                out[:, j] = 1.0
        return out

    def warmup(self) -> None:
        """Pre-touch the codebook."""
        _ = self.codebook @ self.codebook[0]

    def observability(self) -> dict[str, Any]:
        return {
            "metrics": [
                {"name": "braid.catalogstore.semanticids.score.duration", "type": "histogram"},
            ]
        }

    def metrics(self) -> list[Any]:
        return []
