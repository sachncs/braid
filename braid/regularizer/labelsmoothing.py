"""Label smoothing regularizer."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="regularizer", name="labelsmoothing")
class labelsmoothing:
    """Smooth one-hot labels by ``epsilon``."""

    name: str = "labelsmoothing"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset(
        {
            "observable",
        }
    )

    def __init__(self, epsilon: float = 0.1) -> None:
        if not 0 <= epsilon < 1:
            raise ValueError("epsilon must be in [0, 1)")
        self.epsilon = epsilon

    def smooth(self, labels: Any, numclasses: int) -> Any:
        """Smooth integer labels to a soft target distribution."""
        try:
            import torch.nn.functional as F
        except ImportError:
            return labels
        return (
            F.one_hot(labels, numclasses).float() * (1 - self.epsilon) + self.epsilon / numclasses
        )

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
