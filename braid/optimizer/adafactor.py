"""Adafactor optimizer factory."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="optimizer", name="adafactor")
class adafactor:
    """Adafactor optimizer factory (memory-efficient)."""

    name: str = "adafactor"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, lr: float = 1e-3, weightdecay: float = 0.0) -> None:
        self.lr = lr
        self.weightdecay = weightdecay

    def create(self, params) -> Any:
        try:
            from transformers import Adafactor
        except ImportError:
            import torch

            return torch.optim.AdamW(params, lr=self.lr, weight_decay=self.weightdecay)
        return Adafactor(params, lr=self.lr, weight_decay=self.weightdecay)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
