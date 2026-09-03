"""Borda rank aggregator."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from braid.core.registry import registry


@registry.register(category="rankaggregator", name="borda")
class borda:
    """Borda count rank aggregator."""

    name: str = "borda"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def aggregate(self, rankings: list[list[int]]) -> list[int]:
        """Aggregate rankings via Borda count."""
        scores: defaultdict[int, float] = defaultdict(float)
        n = 0
        for ranking in rankings:
            n = max(n, len(ranking))
            for rank, item in enumerate(ranking):
                scores[item] += n - rank
        return sorted(scores.keys(), key=lambda x: -scores[x])

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
