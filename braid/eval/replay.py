"""Replay evaluator (counterfactual online replay)."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="eval", name="replay")
class replayeval:
    """Counterfactual replay evaluator: rank log queries, compare to actual engagement."""

    name: str = "replay"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"replayable", "observable"})

    def __init__(self, topk: int = 50) -> None:
        self.topk = topk

    def evaluate(self, ranker: Any, queries: list[dict[str, Any]]) -> dict[str, float]:
        """Replay ``queries`` through ``ranker`` and measure recall vs actual engagement."""
        from braid.eval.offlineranking import offlineranking

        er = offlineranking()
        predictions: list[list[int]] = []
        truth: list[int] = []
        for q in queries:
            try:
                res = ranker.rank(q.get("prompt", ""), None, topk=self.topk)
                preds = res.get("ids", [])[: self.topk]
            except Exception:  # noqa: BLE001
                preds = list(range(self.topk))
            predictions.append(preds)
            truth.append(int(q.get("itemid", -1)))
        return er.evaluate(predictions, truth)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
