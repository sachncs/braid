"""Chronological train/val/test splitter.

Splits by ratio along the time dimension. No future leakage.
"""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.registry import registry


@registry.register(category="splitter", name="chronological")
class chronologicalsplitter:
    """Split chronologically by ratios.

    Attributes:
        trainratio: portion for training.
        valratio: portion for validation. Remainder is test.
    """

    name: str = "chronological"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"streamable", "observable"})

    def __init__(self, trainratio: float = 0.8, valratio: float = 0.1) -> None:
        if trainratio + valratio >= 1.0:
            raise ValueError("trainratio + valratio must be < 1")
        self.trainratio = trainratio
        self.valratio = valratio

    def split(self, rows: Iterable[dict[str, Any]]) -> tuple[list, list, list]:
        """Split rows into train/val/test.

        Args:
            rows: events with a ``timestamp`` field.

        Returns:
            (train, val, test) lists.
        """
        rows = sorted(rows, key=lambda r: r.get("timestamp", 0))
        n = len(rows)
        ntrain = int(n * self.trainratio)
        nval = int(n * self.valratio)
        return rows[:ntrain], rows[ntrain : ntrain + nval], rows[ntrain + nval :]

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
