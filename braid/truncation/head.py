"""Head (recency) truncation."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="truncation", name="head")
class head:
    """Keep the most recent ``budget`` events."""

    name: str = "head"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, budget: int = 20) -> None:
        self.budget = budget

    def fit(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return the most recent ``budget`` events."""
        return events[-self.budget :]

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"truncation:head:{self.budget}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
