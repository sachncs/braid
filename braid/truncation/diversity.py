"""Diversity-based truncation."""

from __future__ import annotations

from collections import Counter
from typing import Any

from braid.core.registry import registry


@registry.register(category="truncation", name="diversity")
class diversity:
    """Greedy diversity selection: prioritize distinct items."""

    name: str = "diversity"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, budget: int = 30) -> None:
        self.budget = budget

    def fit(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Select greedily to maximize distinct-item count."""
        seen: Counter = Counter()
        out: list[dict[str, Any]] = []
        for ev in reversed(events):
            key = ev.get("itemid")
            if seen[key] >= 2:
                continue
            out.append(ev)
            seen[key] += 1
            if len(out) >= self.budget:
                break
        return list(reversed(out))

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"truncation:diversity:{self.budget}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
