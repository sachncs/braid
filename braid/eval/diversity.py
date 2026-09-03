"""Diversity evaluator."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="eval", name="diversity")
class diversityeval:
    """Intra-list diversity and coverage evaluators."""

    name: str = "diversity"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, k: int = 10) -> None:
        self.k = k

    def evaluate(self, lists: list[list[int]], embeddings: np.ndarray | None = None, universe: list[int] | None = None) -> dict[str, float]:
        """Compute average intra-list distance and catalog coverage."""
        if not lists:
            return {"intra": 0.0, "coverage": 0.0}
        intra: list[float] = []
        coverage: set[int] = set()
        for lst in lists:
            coverage.update(lst[: self.k])
            if embeddings is not None and len(lst) > 1:
                ks = lst[: self.k]
                pairs = [np.dot(embeddings[i], embeddings[j]) for i in ks for j in ks if i != j]
                intra.append(1.0 - float(np.mean(pairs)) if pairs else 0.0)
        cov = 0.0
        if universe:
            cov = len(coverage) / len(universe)
        return {"intra": float(np.mean(intra)) if intra else 0.0, "coverage": cov}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
