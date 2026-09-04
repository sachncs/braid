"""Offline ranking metrics: MRR, NDCG@10, HitRate@10, MAP@10.

The metrics here are computed over binary relevance (rank-with-single-target).
For graded relevance, use :class:`braid.eval.calibration` and friends.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="eval", name="offlineranking")
class offlineranking:
    """Offline ranking metrics over prediction/ground-truth pairs.

    Each (predictions[i], groundtruth[i]) is a single-target ranking problem;
    if a query has multiple targets, split it into multiple rows. Metrics:

    * **MRR** — Mean Reciprocal Rank
    * **NDCG@10** — Normalized Discounted Cumulative Gain @ K=10
    * **HitRate@10** — fraction of queries where the target is in top 10
    * **MAP@10** — Mean Average Precision @ K=10
    """

    name: str = "offlineranking"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def evaluate(
        self,
        predictions: list[list[int]],
        groundtruth: list[int],
        k: int = 10,
    ) -> dict[str, float]:
        """Compute MRR, NDCG@k, HitRate@k, MAP@k.

        Args:
            predictions: per-query ranked lists of item ids.
            groundtruth: per-query target item id (binary relevance).
            k: cutoff for ``HitRate@k`` and ``MAP@k``.

        Returns:
            A dict with ``mrr``, ``ndcg``, ``hitrate``, ``map`` averaged over queries.
        """
        if len(predictions) != len(groundtruth):
            raise ValueError(
                f"predictions ({len(predictions)}) and groundtruth ({len(groundtruth)}) "
                f"must have equal length"
            )
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
            hits.append(1.0 if rank is not None and rank <= k else 0.0)
            if rank is None:
                ndcgs.append(0.0)
            else:
                gains = [1.0 / np.log2(r + 1) for r in range(2, rank + 1)]
                dcg = sum(gains[-1:]) if rank > 1 else 1.0
                idcg = 1.0
                ndcgs.append(dcg / idcg)
            aps: list[float] = []
            hitcount = 0
            for i, p in enumerate(preds[:k]):
                if p == target:
                    hitcount += 1
                    aps.append(hitcount / (i + 1))
            maps.append(sum(aps) / k if aps else 0.0)
        n = len(predictions)
        return {
            "mrr": sum(mrr) / n,
            "ndcg": sum(ndcgs) / n,
            "hitrate": sum(hits) / n,
            "map": sum(maps) / n,
        }

    def observability(self) -> dict[str, Any]:
        return {
            "metrics": [
                {"name": "braid.eval.offlineranking.mrr", "type": "gauge"},
                {"name": "braid.eval.offlineranking.ndcg", "type": "gauge"},
                {"name": "braid.eval.offlineranking.hitrate", "type": "gauge"},
                {"name": "braid.eval.offlineranking.map", "type": "gauge"},
            ]
        }

    def metrics(self) -> list[Any]:
        return []
