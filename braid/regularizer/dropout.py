"""Dropout regularizer."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="regularizer", name="dropout")
class dropout:
    """Standard dropout regularizer (operates on callables)."""

    name: str = "dropout"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, p: float = 0.1) -> None:
        if not 0 <= p < 1:
            raise ValueError("p must be in [0, 1)")
        self.p = p

    def apply(self, x: Any) -> Any:
        """Apply (functional) dropout to ``x`` if torch is available."""
        try:
            import torch
            import torch.nn.functional as F
        except ImportError:
            return x
        return F.dropout(x, p=self.p, training=True)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
