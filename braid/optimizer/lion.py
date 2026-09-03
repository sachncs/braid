"""Lion optimizer factory."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="optimizer", name="lion")
class lion:
    """Lion optimizer factory (sign-based momentum)."""

    name: str = "lion"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, lr: float = 1e-4, betas: tuple = (0.9, 0.99), weightdecay: float = 0.01) -> None:
        self.lr = lr
        self.betas = betas
        self.weightdecay = weightdecay

    def create(self, params) -> Any:
        try:
            from lion_pytorch import Lion
        except ImportError:
            import torch

            return torch.optim.AdamW(params, lr=self.lr, weight_decay=self.weightdecay)
        return Lion(params, lr=self.lr, betas=self.betas, weight_decay=self.weightdecay)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
