"""Reciprocal Rank Fusion aggregator."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from braid.core.registry import registry


@registry.register(category="rankaggregator", name="rrf")
class rrf:
    """Reciprocal Rank Fusion aggregator."""

    name: str = "rrf"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, k: int = 60) -> None:
        self.k = k

    def aggregate(self, rankings: list[list[int]]) -> list[int]:
        """Aggregate by RRF score."""
        scores: defaultdict[int, float] = defaultdict(float)
        for ranking in rankings:
            for rank, item in enumerate(ranking):
                scores[item] += 1.0 / (self.k + rank + 1)
        return sorted(scores.keys(), key=lambda x: -scores[x])

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
