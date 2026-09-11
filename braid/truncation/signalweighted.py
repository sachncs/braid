"""Signal-weighted truncation."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="truncation", name="signalweighted")
class signalweighted:
    """Keep events weighted by their signal strength (duration, rating)."""

    name: str = "signalweighted"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, budget: int = 20) -> None:
        self.budget = budget

    def fit(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Score by signal; keep top ``budget`` events."""

        def score(ev: dict[str, Any]) -> float:
            dur = float(ev.get("duration", 0.0))
            rating = float(ev.get("rating", 0.0))
            kind = ev.get("kind", "play")
            kind_boost = {"thumbup": 2.0, "add": 1.5, "play": 1.0, "click": 0.2}.get(kind, 0.5)
            return dur * kind_boost + rating

        ranked = sorted(events, key=score, reverse=True)
        return ranked[: self.budget]

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"truncation:signalweighted:{self.budget}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
