"""Composite evaluator: aggregate over a list of evaluators."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="eval", name="composite")
class composite:
    """Composes a list of evaluators, merges reports."""

    name: str = "composite"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, members: list[tuple[str, float]] | None = None) -> None:
        self.members = members or [("offlineranking", 1.0), ("calibration", 0.5), ("diversity", 0.5)]
        self._cache: dict[str, Any] = {}

    def evaluate(self, predictions: Any, groundtruth: Any = None, **kwargs: Any) -> dict[str, Any]:
        """Run each member and merge reports."""
        report: dict[str, Any] = {}
        for name, _w in self.members:
            ev = self._cache.get(name) or registry.create("eval", name)
            self._cache[name] = ev
            try:
                if name == "diversity":
                    rep = ev.evaluate(predictions, embeddings=kwargs.get("embeddings"), universe=kwargs.get("universe"))
                elif name == "calibration":
                    rep = ev.evaluate(predictions, groundtruth)
                elif name == "offlineranking":
                    rep = ev.evaluate(predictions, groundtruth)
                elif name == "replay":
                    rep = ev.evaluate(kwargs.get("ranker"), predictions)
                elif name == "interleaving":
                    rep = ev.evaluate(kwargs.get("lista", []), kwargs.get("listb", []), kwargs.get("engagements", []))
                elif name == "baseline":
                    rep = ev.evaluate(predictions, groundtruth, **kwargs)
                else:
                    rep = {}
                report[name] = rep
            except Exception as exc:  # noqa: BLE001
                report[name] = {"error": str(exc)}
        return report

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
