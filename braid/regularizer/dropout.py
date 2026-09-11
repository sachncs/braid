"""Dropout regularizer."""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="regularizer", name="dropout")
class dropout:
    """Standard dropout regularizer over torch tensors."""

    name: str = "dropout"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, p: float = 0.1) -> None:
        if not 0 <= p < 1:
            raise ValueError("p must be in [0, 1)")
        self.p = p

    def apply(self, x: Any) -> Any:
        """Apply dropout to ``x``; raise :class:`requiresenvironment` if torch is missing.

        Args:
            x: a ``torch.Tensor`` of activations.

        Returns:
            The dropout-masked tensor.
        """
        try:
            import torch.nn.functional as F
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for regularizer:dropout",
                hint="pip install torch",
            ) from exc
        return F.dropout(x, p=self.p, training=True)

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.regularizer.dropout.p", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
