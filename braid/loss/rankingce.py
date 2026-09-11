"""Cross-entropy loss over a catalog.

Operates on integer labels (positive item ids); treats negatives as
in-batch or sampled.
"""

from __future__ import annotations

from typing import Any

import torch.nn.functional as F

from braid.core.registry import registry


@registry.register(category="loss", name="rankingce")
class rankingce:
    """Catalog softmax cross-entropy."""

    name: str = "rankingce"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset(
        {
            "observable",
        }
    )

    def __init__(self, labelSmoothing: float = 0.0) -> None:
        self.labelSmoothing = labelSmoothing

    def compute(self, scores: Any, labels: Any, weight: float = 1.0) -> Any:
        """Compute cross-entropy.

        Args:
            scores: ``[batch, numitems]`` logits.
            labels: ``[batch]`` positive item ids.
            weight: scalar multiplier.

        Returns:
            Scalar loss value (tensor).
        """
        loss = F.cross_entropy(scores, labels, label_smoothing=self.labelSmoothing)
        return weight * loss

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.loss.rankingce", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
