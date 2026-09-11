"""AdamW optimizer factory."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="optimizer", name="adamw")
class adamw:
    """AdamW optimizer factory."""

    name: str = "adamw"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset(
        {
            "observable",
        }
    )

    def __init__(
        self, lr: float = 1e-4, betas: tuple = (0.9, 0.999), weightdecay: float = 0.01
    ) -> None:
        self.lr = lr
        self.betas = betas
        self.weightdecay = weightdecay

    def create(self, params) -> Any:
        """Return a torch ``AdamW`` instance."""
        try:
            import torch
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("pytorch required for adamw") from exc
        return torch.optim.AdamW(
            params, lr=self.lr, betas=self.betas, weight_decay=self.weightdecay
        )

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
