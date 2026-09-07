"""Adafactor optimizer factory. Requires ``transformers``."""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="optimizer", name="adafactor")
class adafactor:
    """Adafactor optimizer factory (memory-efficient)."""

    name: str = "adafactor"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, lr: float = 1e-3, weightdecay: float = 0.0) -> None:
        self.lr = lr
        self.weightdecay = weightdecay

    def create(self, params: Any) -> Any:
        """Return an Adafactor optimizer or raise."""
        try:
            from transformers import Adafactor

            return Adafactor(params, lr=self.lr, weight_decay=self.weightdecay)
        except ImportError as exc:
            raise requiresenvironment(
                "transformers is required for optimizer:adafactor",
                hint="pip install transformers",
            ) from exc

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
