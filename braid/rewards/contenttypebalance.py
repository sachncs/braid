"""Content-type balance reward."""

from __future__ import annotations

from collections import Counter
from typing import Any

from braid.rewards.signals import register


@register("contenttypebalance")
class contenttypebalance:
    """Boosts under-represented content types in a batch.

    Attributes:
        targetmix: dict of type -> target proportion.
    """

    name: str = "contenttypebalance"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, targetmix: dict[str, float] | None = None) -> None:
        self.targetmix = targetmix or {"movie": 0.7, "show": 0.2, "game": 0.05, "live": 0.05}

    def score(self, event: dict[str, Any], history: list[dict[str, Any]] | None = None) -> float:
        """Higher for under-represented types."""
        history = history or []
        if not history:
            return self.targetmix.get(event.get("kind", "movie"), 0.0)
        ctype = event.get("contenttype", "movie")
        counts = Counter(e.get("contenttype", "movie") for e in history)
        current = counts.get(ctype, 0) / max(len(history), 1)
        target = self.targetmix.get(ctype, 0.0)
        return max(0.0, target - current)

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"reward:contenttypebalance:v1"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
