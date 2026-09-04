"""Contrastive (InfoNCE-style) negative miner."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="miner", name="contrastiveminer")
class contrastiveminer:
    """Mine negatives by similarity in the embedding space."""

    name: str = "contrastiveminer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, k: int = 64, temperature: float = 1.0) -> None:
        self.k = k
        self.temperature = temperature

    def mine(self, positives: Any, embeddings: Any) -> Any:
        """Mine by picking top-K similar items per row."""
        try:
            import torch
        except ImportError:
            return []
        norm = torch.nn.functional.normalize(embeddings, dim=-1)
        sim = norm @ norm.T
        return sim.topk(self.k, dim=-1).indices

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
