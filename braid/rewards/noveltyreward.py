"""Novelty reward — boosts fresh items; real age-aware scoring."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="reward", name="noveltyreward")
class noveltyreward:
    """Reward that boosts recently launched items.

    Attributes:
        noveltymaxage: days since launch for the novelty window.
    """

    name: str = "noveltyreward"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, noveltymaxage: int = 14) -> None:
        if noveltymaxage <= 0:
            raise ValueError("noveltymaxage must be > 0")
        self.noveltymaxage = noveltymaxage

    def score(self, event: dict[str, Any], ctx: dict[str, Any] | None = None) -> float:
        """Return 1.0 if the item is fresh, 0.0 if stale, scaled between.

        Args:
            event: the candidate event (must include ``launcheddays``).
            ctx: unused.

        Returns:
            Float in ``[0, 1]``.
        """
        launched = event.get("launcheddays", 9999)
        if launched >= self.noveltymaxage:
            return 0.0
        return (self.noveltymaxage - launched) / self.noveltymaxage

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
