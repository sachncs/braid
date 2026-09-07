"""Composite evaluator: aggregate over a list of evaluators.

Each (name, weight) pair is resolved through the registry, invoked, and the
result is merged into a single report with a weighted scalar ``score`` for
comparing configurations.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="eval", name="composite")
class composite:
    """Composes a list of evaluators, merges reports."""

    name: str = "composite"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(
        self,
        members: list[tuple[str, float]] | None = None,
    ) -> None:
        self.members = members or [
            ("offlineranking", 1.0),
            ("calibration", 0.5),
            ("diversity", 0.5),
        ]
        self.cache: dict[str, Any] = {}

    def evaluate(self, predictions: Any, groundtruth: Any = None, **kwargs: Any) -> dict[str, Any]:
        """Run each member and merge reports.

        Args:
            predictions: per-query predictions or, for ``diversity``, ranked lists.
            groundtruth: per-query target item id.
            kwargs: forwarded keyword arguments (e.g. ``embeddings``, ``universe``,
                ``ranker``, ``lista``, ``listb``, ``engagements``).

        Returns:
            A merged report with a weighted scalar ``score``.
        """
        report: dict[str, Any] = {}
        scalar_total = 0.0
        weight_total = 0.0
        for name, weight in self.members:
            ev = self.cache.get(name) or registry.create("eval", name)
            self.cache[name] = ev
            try:
                if name == "diversity":
                    rep = ev.evaluate(predictions, embeddings=kwargs.get("embeddings"), universe=kwargs.get("universe"))
                elif name in {"calibration", "offlineranking"}:
                    rep = ev.evaluate(predictions, groundtruth)
                elif name == "replay":
                    rep = ev.evaluate(kwargs.get("ranker"), predictions)
                elif name == "interleaving":
                    rep = ev.evaluate(
                        kwargs.get("lista", []), kwargs.get("listb", []), kwargs.get("engagements", [])
                    )
                elif name == "baseline":
                    rep = ev.evaluate(predictions, groundtruth, **kwargs)
                else:
                    rep = {}
                report[name] = rep
                scalar_total += weight * _scalarize(rep)
                weight_total += weight
            except Exception as exc:  # noqa: BLE001 — composite isolates evaluator errors
                report[name] = {"error": str(exc)}
        report["score"] = scalar_total / weight_total if weight_total else 0.0
        return report

    def observability(self) -> dict[str, Any]:
        return {
            "metrics": [
                {"name": "braid.eval.composite.score", "type": "gauge"},
            ]
        }

    def metrics(self) -> list[Any]:
        return []


def _scalarize(report: dict[str, Any]) -> float:
    """Pick a scalar representative of a per-evaluator report.

    Tries the standard ``mrr``, ``ndcg``, ``score`` keys then any first float it
    finds.
    """
    for k in ("mrr", "ndcg", "score", "ece", "intra"):
        if k in report:
            try:
                return float(report[k])
            except (TypeError, ValueError):
                continue
    for v in report.values():
        if isinstance(v, (int, float)):
            return float(v)
    return 0.0
