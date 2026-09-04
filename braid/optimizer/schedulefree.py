"""Schedule-free optimizer factory. Requires ``schedulefree``."""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="optimizer", name="schedulefree")
class schedulefree:
    """Schedule-free AdamW optimizer factory."""

    name: str = "schedulefree"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, lr: float = 1e-3, weightdecay: float = 0.01) -> None:
        self.lr = lr
        self.weightdecay = weightdecay

    def create(self, params: Any) -> Any:
        """Return a schedule-free AdamW optimizer or raise."""
        try:
            from schedulefree import AdamWScheduleFree

            return AdamWScheduleFree(params, lr=self.lr, weight_decay=self.weightdecay)
        except ImportError as exc:
            raise requiresenvironment(
                "schedulefree is required for optimizer:schedulefree",
                hint="pip install schedulefree",
            ) from exc

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
