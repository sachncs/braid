"""Elbow-point truncation.

Picks events up to a known elbow point (computed offline).
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="truncation", name="elbow")
class elbow:
    """Keep events up to a precomputed elbow point.

    Attributes:
        elbowevents: number of events at the elbow point.
    """

    name: str = "elbow"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, elbowevents: int = 30) -> None:
        self.elbowevents = elbowevents

    def fit(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return events[-self.elbowevents :]

    def setelbow(self, n: int) -> None:
        """Update the elbow point."""
        self.elbowevents = n

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"truncation:elbow:{self.elbowevents}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
