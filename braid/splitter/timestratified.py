"""Time-stratified splitter.

Stratifies events across time buckets so that train/val/test cover all
buckets proportionally.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from braid.core.registry import registry


@registry.register(category="splitter", name="timestratified")
class timestratifiedsplitter:
    """Stratify by time bucket before splitting.

    Attributes:
        nbuckets: number of time buckets.
        trainratio: portion for training.
        valratio: portion for validation.
    """

    name: str = "timestratified"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"streamable", "observable"})

    def __init__(self, nbuckets: int = 10, trainratio: float = 0.8, valratio: float = 0.1) -> None:
        self.nbuckets = nbuckets
        self.trainratio = trainratio
        self.valratio = valratio

    def split(self, rows: Iterable[dict[str, Any]]) -> tuple[list, list, list]:
        """Stratify by time bucket then split each bucket."""
        rows = list(rows)
        if not rows:
            return [], [], []
        timestamps = [float(r.get("timestamp", 0)) for r in rows]
        tmin, tmax = min(timestamps), max(timestamps)
        spread = max(tmax - tmin, 1.0)
        bucketed: dict[int, list[Any]] = defaultdict(list)
        for r in rows:
            ts = float(r.get("timestamp", 0))
            bidx = int(((ts - tmin) / spread) * (self.nbuckets - 1)) if spread > 0 else 0
            bucketed[bidx].append(r)
        train: list[Any] = []
        val: list[Any] = []
        test: list[Any] = []
        for _, evs in sorted(bucketed.items()):
            evs = sorted(evs, key=lambda r: r.get("timestamp", 0))
            n = len(evs)
            ntrain = int(n * self.trainratio)
            nval = int(n * self.valratio)
            train.extend(evs[:ntrain])
            val.extend(evs[ntrain : ntrain + nval])
            test.extend(evs[ntrain + nval :])
        return train, val, test

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
