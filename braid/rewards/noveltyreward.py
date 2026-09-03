"""Novelty reward (cold-start exploration)."""

from __future__ import annotations

from typing import Any

from braid.rewards.signals import register


@register("noveltyreward")
class noveltyreward:
    """Reward that boosts fresh or recently launched items."""

    name: str = "noveltyreward"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, noveltymaxage: int = 14) -> None:
        """Days since launch used as the novelty window."""
        self.noveltymaxage = noveltymaxage

    def score(self, event: dict[str, Any], ctx: dict[str, Any] | None = None) -> float:
        """Returns 1.0 if the item is fresh; 0.0 if stale."""
        launched = event.get("launcheddays", 9999)
        if launched >= self.noveltymaxage:
            return 0.0
        return (self.noveltymaxage - launched) / self.noveltymaxage

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"reward:noveltyreward:{self.noveltymaxage}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
