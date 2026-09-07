"""Random negative miner.

Uniformly samples negative item ids from the catalog.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="miner", name="random")
class random:
    """Uniformly sample negative item ids per positive.

    Attributes:
        numitems: catalog size.
        k: negatives per positive.
        seed: RNG seed.
    """

    name: str = "random"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, numitems: int, k: int = 64, seed: int = 0) -> None:
        if numitems <= 0:
            raise ValueError("numitems must be > 0")
        if k <= 0:
            raise ValueError("k must be > 0")
        self.numitems = numitems
        self.k = k
        self.seed = seed

    def mine(self, positives: Any, scoresfn: Any | None = None) -> Any:
        """Sample k negatives per positive.

        Args:
            positives: ``[batch]`` tensor or list of positive item ids.
            scoresfn: optional scoring function (unused for random mining).

        Returns:
            ``[batch, k]`` int64 tensor of negative item ids (or list if torch is unavailable).
        """
        try:
            import torch

            g = torch.Generator().manual_seed(self.seed)
            n = positives.shape[0] if hasattr(positives, "shape") else len(positives)
            return torch.randint(0, self.numitems, (n, self.k), generator=g)
        except ImportError:
            import random as r

            rnd = r.Random(self.seed)
            n = len(positives)
            return [[rnd.randrange(self.numitems) for _ in range(self.k)] for _ in range(n)]

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
