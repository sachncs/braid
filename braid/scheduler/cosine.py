"""Cosine LR scheduler factory."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="scheduler", name="cosine")
class cosine:
    """Cosine decay LR scheduler."""

    name: str = "cosine"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, maxsteps: int, minratio: float = 0.0) -> None:
        self.maxsteps = maxsteps
        self.minratio = minratio

    def create(self, optimizer: Any) -> Any:
        try:
            import torch
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("pytorch required for cosine scheduler") from exc
        return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=self.maxsteps, eta_min=self.minratio * optimizer.defaults["lr"])

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
