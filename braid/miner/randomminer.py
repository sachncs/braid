"""Random negative miner."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="miner", name="randomminer")
class randomminer:
    """Uniformly sample negative item ids."""

    name: str = "randomminer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, numitems: int, k: int = 64, seed: int = 0) -> None:
        self.numitems = numitems
        self.k = k
        self.seed = seed

    def mine(self, positives: Any, scoresfn: Any | None = None) -> Any:
        """Sample k negatives per positive."""
        try:
            import torch
        except ImportError:
            return []
        g = torch.Generator().manual_seed(self.seed)
        n = positives.shape[0] if hasattr(positives, "shape") else len(positives)
        return torch.randint(0, self.numitems, (n, self.k), generator=g)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
