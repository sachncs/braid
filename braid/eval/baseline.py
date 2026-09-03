"""Baseline comparison evaluator (vs TF-IDF, popularity, random)."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="eval", name="baseline")
class baseline:
    """Compare to baselines: random, popularity, TF-IDF."""

    name: str = "baseline"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def evaluate(self, predictions: list[list[int]], groundtruth: list[int], numitems: int = 1000, popularity: np.ndarray | None = None) -> dict[str, Any]:
        """Compare ``predictions`` to a random baseline and popularity (if provided)."""
        from braid.eval.offlineranking import offlineranking

        rng = np.random.default_rng(0)
        randompreds = [rng.choice(numitems, size=len(p), replace=False).tolist() for p in predictions]
        randmetrics = offlineranking().evaluate(randompreds, groundtruth)
        popularitypreds = []
        if popularity is not None:
            p = np.asarray(popularity, dtype=np.float64)
            top = np.argsort(-p)
            for _ in predictions:
                popularitypreds.append(top[: len(predictions[0])].tolist())
            popmetrics = offlineranking().evaluate(popularitypreds, groundtruth)
        else:
            popmetrics = {}
        ours = offlineranking().evaluate(predictions, groundtruth)
        return {"ours": ours, "random": randmetrics, "popularity": popmetrics}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
