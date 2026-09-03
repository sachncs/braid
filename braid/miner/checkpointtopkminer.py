"""Checkpoint top-K miner.

Mines hard negatives from the top-K predictions of a previous checkpoint.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="miner", name="checkpointtopkminer")
class checkpointtopkminer:
    """Hard negatives from a previous checkpoint's top-K predictions."""

    name: str = "checkpointtopkminer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, k: int = 64) -> None:
        self.k = k

    def mine(self, positives: Any, scoresfn: Any) -> Any:
        """Mine hard negatives using ``scoresfn``."""
        try:
            import torch
        except ImportError:
            return []
        scores = scoresfn()
        topk = scores.topk(self.k, dim=-1).indices
        return topk

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
