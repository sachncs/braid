"""Diversity postprocessor using MMR."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="resppost", name="diversity")
class diversity:
    """Maximal-marginal-relevance diversity re-rank."""

    name: str = "diversity"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, lam: float = 0.5) -> None:
        if not 0 <= lam <= 1:
            raise ValueError("lam must be in [0, 1]")
        self.lam = lam

    def process(self, response: dict[str, Any], embeddings: np.ndarray | None = None) -> dict[str, Any]:
        """Apply MMR-style diversity on the top-k."""
        ids = response.get("ids", [])
        scores = response.get("scores", [])
        if embeddings is None or len(ids) < 2:
            return response
        order = list(range(len(ids)))
        selected: list[int] = [order[0]]
        while len(selected) < len(order):
            bestscore = -1e9
            bestj = order[-1]
            for j in order:
                if j in selected:
                    continue
                rel = scores[j]
                div = max(float(np.dot(embeddings[ids[j]], embeddings[ids[k]])) for k in selected)
                mmr = self.lam * rel - (1 - self.lam) * div
                if mmr > bestscore:
                    bestscore = mmr
                    bestj = j
            selected.append(bestj)
        return {
            "ids": [ids[j] for j in selected],
            "scores": [scores[j] for j in selected],
        }

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
