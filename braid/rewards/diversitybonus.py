"""Diversity bonus reward."""

from __future__ import annotations

from collections import Counter
from typing import Any

from braid.rewards.signals import register


@register("diversitybonus")
class diversitybonus:
    """Rewards events whose item is rare in the user's recent history.

    Attributes:
        recentk: how many recent events to consider.
    """

    name: str = "diversitybonus"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, recentk: int = 50) -> None:
        self.recentk = recentk

    def score(self, event: dict[str, Any], history: list[dict[str, Any]] | None = None) -> float:
        """Higher for rarer items."""
        history = history or []
        recent = history[-self.recentk :]
        counts = Counter(e.get("itemid") for e in recent)
        seen = counts.get(event.get("itemid"), 0)
        if not recent:
            return 1.0
        return 1.0 - (seen / len(recent))

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"reward:diversitybonus:{self.recentk}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
