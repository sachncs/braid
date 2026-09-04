"""In-batch negative miner.

Treats every other item in the batch as a negative for the current
positive.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="miner", name="inbatch")
class inbatch:
    """In-batch negative miner.

    Each item in the batch serves as a negative for every other item.
    """

    name: str = "inbatch"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def mine(self, positives: Any, scoresfn: Any | None = None) -> Any:
        """Return in-batch negatives.

        Args:
            positives: ``[batch]`` positive item ids.
            scoresfn: unused.

        Returns:
            ``[batch, batch-1]`` int64 tensor of negatives per row.
        """
        try:
            import torch

            n = positives.shape[0] if hasattr(positives, "shape") else len(positives)
            idx = torch.arange(n).unsqueeze(0).repeat(n, 1)
            mask = idx != torch.arange(n).unsqueeze(1)
            return idx[mask].reshape(n, n - 1)
        except ImportError:
            return [([j for j in range(len(positives)) if j != i]) for i in range(len(positives))]

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
