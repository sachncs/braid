"""Lion optimizer factory. Requires ``lion_pytorch`` (optional)."""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="optimizer", name="lion")
class lion:
    """Lion optimizer factory (sign-based momentum)."""

    name: str = "lion"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(
        self, lr: float = 1e-4, betas: tuple = (0.9, 0.99), weightdecay: float = 0.01
    ) -> None:
        self.lr = lr
        self.betas = betas
        self.weightdecay = weightdecay

    def create(self, params: Any) -> Any:
        """Return a Lion optimizer or raise."""
        try:
            from lion_pytorch import Lion

            return Lion(params, lr=self.lr, betas=self.betas, weight_decay=self.weightdecay)
        except ImportError as exc:
            raise requiresenvironment(
                "lion_pytorch is required for optimizer:lion",
                hint="pip install lion-pytorch",
            ) from exc

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
