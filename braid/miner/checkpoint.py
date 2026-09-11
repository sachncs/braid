"""Checkpoint top-K miner.

Mines hard negatives from a previous checkpoint's top-K predictions.
Score function is supplied externally.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="miner", name="checkpoint")
class checkpoint:
    """Mines hard negatives using a previously computed score function.

    Attributes:
        k: number of top items to use as hard negatives.
    """

    name: str = "checkpoint"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, k: int = 64) -> None:
        if k <= 0:
            raise ValueError("k must be > 0")
        self.k = k

    def mine(self, positives: Any, scoresfn: Any) -> Any:
        """Compute hard negatives from ``scoresfn``.

        Args:
            positives: ``[batch]`` positive item ids (unused; positives are
                the targets the score function was trained on).
            scoresfn: callable returning a ``[batch, numitems]`` score tensor.

        Returns:
            ``[batch, k]`` int64 tensor of hard-negative ids per row.
        """

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
