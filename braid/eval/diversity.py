"""Diversity evaluator — intra-list dissimilarity, catalog coverage and gini-style spread.

These scores quantify whether the ranker is producing lists that cover the catalog
broadly rather than collapsing onto a narrow set of popular items, computed as:

* **intra** — mean pairwise cosine distance among the top-K positions of every list.
* **coverage** — fraction of the catalog universe that appears in any top-K across queries.
* **gini** — Gini coefficient over item-occurrence counts (lower = more even).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="eval", name="diversity")
class diversity:
    """Intra-list diversity, catalog coverage and occurrence gini evaluator."""

    name: str = "diversity"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, k: int = 10) -> None:
        self.k = k

    def evaluate(
        self,
        lists: list[list[int]],
        embeddings: np.ndarray | None = None,
        universe: list[int] | None = None,
    ) -> dict[str, float]:
        """Compute mean intra-list distance, catalog coverage, and gini.

        Args:
            lists: per-query ranked item-id lists.
            embeddings: optional 2-D array of item embeddings; row ``i`` is item ``i``'s embedding.
            universe: optional full set of catalog item ids for coverage.

        Returns:
            A dict with ``intra``, ``coverage``, ``gini``.
        """
        if not lists:
            return {"intra": 0.0, "coverage": 0.0, "gini": 0.0}
        intra: list[float] = []
        occ: dict[int, int] = {}
        for lst in lists:
            top = lst[: self.k]
            for i in top:
                occ[i] = occ.get(i, 0) + 1
            if embeddings is not None and len(top) > 1:
                vectors = np.stack([embeddings[i] for i in top], axis=0)
                norms = np.linalg.norm(vectors, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                normalized = vectors / norms
                sims = normalized @ normalized.T
                iu, jv = np.triu_indices(len(top), k=1)
                pairs = sims[iu, jv]
                if pairs.size:
                    intra.append(1.0 - float(np.mean(pairs)))
        coverage = 0.0
        if universe:
            universe_set = set(int(u) for u in universe)
            coverage = len(set(occ.keys()) & universe_set) / max(1, len(universe_set))
        gini = _gini(np.array(list(occ.values()), dtype=np.float64)) if occ else 0.0
        return {
            "intra": float(np.mean(intra)) if intra else 0.0,
            "coverage": coverage,
            "gini": gini,
        }

    def observability(self) -> dict[str, Any]:
        return {
            "metrics": [
                {"name": "braid.eval.diversity.intra", "type": "gauge"},
                {"name": "braid.eval.diversity.coverage", "type": "gauge"},
                {"name": "braid.eval.diversity.gini", "type": "gauge"},
            ]
        }

    def metrics(self) -> list[Any]:
        return []


def _gini(counts: np.ndarray) -> float:
    """Return the Gini coefficient over integer counts (0 for empty)."""
    if counts.size == 0:
        return 0.0
    counts = np.sort(counts)
    n = counts.size
    cum = np.cumsum(counts)
    s = float(cum[-1])
    if s == 0.0:
        return 0.0
    l = (np.arange(1, n + 1) * counts).sum()
    return float(2.0 * l / (n * s) - (n + 1) / n)
