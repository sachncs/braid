"""Condorcet method rank aggregator."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from braid.core.registry import registry


@registry.register(category="rankaggregator", name="condorcet")
class condorcet:
    """Condorcet pairwise aggregator."""

    name: str = "condorcet"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def aggregate(self, rankings: list[list[int]]) -> list[int]:
        """Aggregate via pairwise majority."""
        wins: defaultdict[int, int] = defaultdict(int)
        items: set[int] = set()
        for r in rankings:
            items.update(r)
        for r in rankings:
            for i, a in enumerate(r):
                for b in r[i + 1 :]:
                    wins[a] += 1
        return sorted(items, key=lambda x: -wins[x])

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
