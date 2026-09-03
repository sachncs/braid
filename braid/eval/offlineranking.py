"""Offline ranking metrics: MRR, NDCG, HitRate, MAP."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="eval", name="offlineranking")
class offlineranking:
    """Offline ranking metrics over prediction/ground-truth pairs."""

    name: str = "offlineranking"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def evaluate(self, predictions: list[list[int]], groundtruth: list[int]) -> dict[str, float]:
        """Compute MRR, NDCG@10, HitRate@10, MAP@10."""
        if not predictions:
            return {"mrr": 0.0, "ndcg": 0.0, "hitrate": 0.0, "map": 0.0}
        mrr: list[float] = []
        ndcgs: list[float] = []
        hits: list[float] = []
        maps: list[float] = []
        for preds, target in zip(predictions, groundtruth):
            rank: float | None = None
            for i, p in enumerate(preds):
                if p == target:
                    rank = i + 1
                    break
            mrr.append(0.0 if rank is None else 1.0 / rank)
            hits.append(1.0 if rank is not None and rank <= 10 else 0.0)
            ndcgs.append(0.0 if rank is None else 1.0 / np.log2(rank + 1))
            aps: list[float] = []
            hitcount = 0
            for i, p in enumerate(preds[:10]):
                if p == target:
                    hitcount += 1
                    aps.append(hitcount / (i + 1))
            maps.append(sum(aps) / 1 if aps else 0.0)
        n = len(predictions)
        return {
            "mrr": sum(mrr) / n,
            "ndcg": sum(ndcgs) / n,
            "hitrate": sum(hits) / n,
            "map": sum(maps) / n,
        }

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.eval.offlineranking.mrr", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
