"""Diversity-entropy regularizer.

Penalizes a peaked score distribution to encourage catalog diversity.
"""

from __future__ import annotations

from typing import Any

import torch.nn.functional as F

from braid.core.registry import registry


@registry.register(category="loss", name="diversityentropy")
class diversityentropy:
    """Negative-entropy regularizer on the score distribution."""

    name: str = "diversityentropy"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self) -> None:
        """No parameters."""

    def compute(self, scores: Any, weight: float = 1.0) -> Any:
        """Return negative entropy of softmax(scores).

        Args:
            scores: ``[batch, numitems]`` logits.
            weight: scalar multiplier.

        Returns:
            Scalar tensor.
        """
        probs = F.softmax(scores, dim=-1)
        entropy = -(probs * (probs + 1e-8).log()).sum(dim=-1).mean()
        return weight * (-entropy)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
