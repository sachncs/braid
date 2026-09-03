"""RQ-VAE catalog store.

Stores items as discrete semantic IDs. Decodes query into semantic IDs
and scores via codebook dot product.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="catalogstore", name="rqvaestore")
class rqvaestore:
    """RQ-VAE semantic-ID catalog store.

    Attributes:
        codebook: ``[codebooksize, dim]`` array.
        itemids: list of semantic IDs per item.
    """

    name: str = "rqvaestore"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"speculative", "async", "observable"})

    def __init__(self, codebook: np.ndarray, itemids: list[list[int]]) -> None:
        self.codebook = np.asarray(codebook, dtype=np.float32)
        self.itemids = itemids
        self.numitems = len(itemids)
        self.dim = self.codebook.shape[1]

    def score(self, userrepr: np.ndarray, ids: np.ndarray | None = None) -> np.ndarray:
        """Score by decoding top tokens and matching items.

        Naive implementation: for each row of ``userrepr``, pick the top
        codebook index per code-position and intersect with item ids.
        """
        if ids is None:
            ids = np.arange(self.numitems)
        batch = userrepr.shape[0]
        codes = self.codebook  # [codesize, dim]
        flat = userrepr @ codes.T  # [batch, codesize]
        top = flat.argmax(axis=-1)  # [batch]
        # Match items whose first code contains top.
        matches = np.zeros((batch, len(ids)), dtype=np.float32)
        idxlist = ids.tolist()
        for j, iid in enumerate(idxlist):
            seq = self.itemids[iid]
            if seq and top[0] in seq[:1]:
                matches[:, j] = 1.0
        return matches

    def warmup(self) -> None:
        _ = self.score(np.zeros((1, self.dim), dtype=np.float32), np.arange(min(2, self.numitems)))

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.catalogstore.rqvae.tokens", "type": "histogram"}]}

    def metrics(self) -> list[Any]:
        return []
