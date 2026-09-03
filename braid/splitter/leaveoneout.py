"""Leave-one-out splitter (per-user last N events)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from braid.core.registry import registry


@registry.register(category="splitter", name="leaveoneout")
class leaveoneoutsplitter:
    """Per-user hold out last ``k`` events as test; prior as train.

    Attributes:
        k: number of recent events per user to use as test.
    """

    name: str = "leaveoneout"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"streamable", "observable"})

    def __init__(self, k: int = 1) -> None:
        if k <= 0:
            raise ValueError("k must be > 0")
        self.k = k

    def split(self, rows: Iterable[dict[str, Any]]) -> tuple[list, list, list]:
        """Split into (train, val, test) by per-user last-k hold-out."""
        grouped: dict[Any, list[Any]] = defaultdict(list)
        for r in rows:
            grouped[r.get("userid")].append(r)
        train: list[Any] = []
        test: list[Any] = []
        val: list[Any] = []
        for user, evs in grouped.items():
            evs = sorted(evs, key=lambda r: r.get("timestamp", 0))
            if len(evs) <= self.k:
                train.extend(evs)
                continue
            train.extend(evs[: -self.k])
            test.extend(evs[-self.k :])
            if len(evs) > 2 * self.k:
                val.extend(evs[-2 * self.k : -self.k])
        return train, val, test

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
