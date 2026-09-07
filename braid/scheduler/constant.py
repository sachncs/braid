"""Constant LR scheduler."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="scheduler", name="constant")
class constant:
    """A no-decay constant LR."""

    name: str = "constant"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def create(self, optimizer: Any) -> Any:
        try:
            import torch
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("pytorch required") from exc
        return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lambda step: 1.0)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
