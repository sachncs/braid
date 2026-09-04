"""Replay evaluator (counterfactual online replay).

Takes a historical query log and the items that were actually engaged with,
then runs the proposed ranker over the prompts and measures how much of the
engaged-with material it would have surfaced.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="eval", name="replay")
class replay:
    """Counterfactual replay evaluator.

    For each query, a ranker (any object exposing ``rank(prompt, context, topk) -> {'ids': [...]}``)
    is invoked offline. The returned id list is scored against ``itemid``, the
    actually-engaged-with item. The aggregate metrics are MRR / NDCG@10 /
    HitRate@10 / MAP@10 (delegated to :class:`offlineranking`).
    """

    name: str = "replay"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"replayable", "observable"})

    def __init__(self, topk: int = 50) -> None:
        self.topk = topk

    def evaluate(self, ranker: Any, queries: list[dict[str, Any]]) -> dict[str, float]:
        """Replay ``queries`` through ``ranker`` and report ranking metrics.

        Args:
            ranker: any object with ``rank(prompt: str, context, topk: int) -> {'ids': [...]}``.
            queries: list of dicts each having ``prompt`` and ``itemid`` keys.

        Returns:
            A dict with ``mrr``, ``ndcg``, ``hitrate``, ``map``.
        """
        from braid.eval.offlineranking import offlineranking

        er = offlineranking()
        predictions: list[list[int]] = []
        truth: list[int] = []
        for q in queries:
            try:
                res = ranker.rank(q.get("prompt", ""), None, topk=self.topk)
                preds = list(res.get("ids", []))[: self.topk]
            except Exception:  # noqa: BLE001 — replay harness isolates ranker failures
                preds = list(range(self.topk))
            predictions.append(preds)
            truth.append(int(q.get("itemid", -1)))
        return er.evaluate(predictions, truth)

    def observability(self) -> dict[str, Any]:
        return {
            "metrics": [
                {"name": "braid.eval.replay.mrr", "type": "gauge"},
                {"name": "braid.eval.replay.hitrate", "type": "gauge"},
            ]
        }

    def metrics(self) -> list[Any]:
        return []
