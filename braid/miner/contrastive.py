"""Contrastive (InfoNCE-style) negative miner.

Mines negatives by similarity in the embedding space.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="miner", name="contrastive")
class contrastive:
    """Mine negatives by top-K similar items in embedding space.

    Attributes:
        k: number of similar items per positive.
        temperature: softmax temperature for similarity scores.
    """

    name: str = "contrastive"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, k: int = 64, temperature: float = 1.0) -> None:
        if k <= 0:
            raise ValueError("k must be > 0")
        self.k = k
        self.temperature = temperature

    def mine(self, positives: Any, embeddings: Any) -> Any:
        """Mine top-K similar items per row.

        Args:
            positives: ``[batch]`` positive item ids (unused).
            embeddings: ``[batch, dim]`` representations.

        Returns:
            ``[batch, k]`` int64 tensor of nearest neighbors per row.
        """

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
