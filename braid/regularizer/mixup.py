"""Mixup regularizer."""

from __future__ import annotations

from typing import Any, Tuple

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="regularizer", name="mixup")
class mixup:
    """Mixup data augmentation over torch tensors."""

    name: str = "mixup"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, alpha: float = 0.2) -> None:
        if alpha < 0:
            raise ValueError("alpha must be >= 0")
        self.alpha = alpha

    def mix(self, x: Any, y: Any) -> Tuple[Any, Any, float]:
        """Mix ``x`` with a random partner; raise :class:`requiresenvironment` if torch missing.

        Args:
            x: input batch tensor.
            y: target batch tensor.

        Returns:
            ``(mixed_x, mixed_y, lam)``.
        """
        try:
            import torch
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for regularizer:mixup",
                hint="pip install torch",
            ) from exc
        lam = float(torch.distributions.Beta(self.alpha, self.alpha).sample())
        idx = torch.randperm(x.size(0))
        mixedx = lam * x + (1 - lam) * x[idx]
        mixedy = lam * y + (1 - lam) * y[idx]
        return mixedx, mixedy, lam

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
