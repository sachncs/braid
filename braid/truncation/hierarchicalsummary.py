"""Hierarchical summary truncation.

Compresses long sequences by retaining high-signal events and replacing
the rest with a summary phrase.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="truncation", name="hierarchicalsummary")
class hierarchicalsummary:
    """Compress events with a top-N hot + summarized tail."""

    name: str = "hierarchicalsummary"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, budget: int = 30, hotk: int = 5) -> None:
        self.budget = budget
        self.hotk = hotk

    def fit(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Keep last ``hotk`` + signal-weighted top; summarize rest."""

        def score(ev: dict[str, Any]) -> float:
            return float(ev.get("duration", 0.0)) + float(ev.get("rating", 0.0))

        if len(events) <= self.budget:
            return events
        recent = events[-self.hotk :]
        middle = events[: -self.hotk]
        ranked = sorted(middle, key=score, reverse=True)[: self.budget - self.hotk]
        summary = [{"summary": f"+{len(middle) - len(ranked)} earlier events"}]
        return ranked + recent + summary

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"truncation:hierarchicalsummary:{self.budget}:{self.hotk}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
