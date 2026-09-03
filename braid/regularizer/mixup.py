"""Mixup regularizer."""

from __future__ import annotations

from typing import Any, Tuple

from braid.core.registry import registry


@registry.register(category="regularizer", name="mixup")
class mixup:
    """Mixup data augmentation."""

    name: str = "mixup"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, alpha: float = 0.2) -> None:
        if alpha < 0:
            raise ValueError("alpha must be >= 0")
        self.alpha = alpha

    def mix(self, x: Any, y: Any) -> Tuple[Any, Any, float]:
        """Mix a batch with a sampled partner."""
        try:
            import torch
        except ImportError:
            return x, y, 1.0
        lam = float(torch.distributions.Beta(self.alpha, self.alpha).sample())
        idx = torch.randperm(x.size(0))
        mixedx = lam * x + (1 - lam) * x[idx]
        return mixedx, (y, y[idx], lam), lam

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
