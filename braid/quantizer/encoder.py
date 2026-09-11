"""Quantizer encoder — trainable MLP projecting to the latent."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn  # noqa: F401 — used in body via nn alias

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="quantizer", name="encoder")
class encoder:
    """Trainable MLP encoder.

    Projects ``[batch, inputdim]`` → ``[batch, hiddendim]``.
    """

    name: str = "encoder"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, inputdim: int = 64, hiddendim: int = 128) -> None:
        if inputdim <= 0 or hiddendim <= 0:
            raise ValueError("dims must be > 0")
        try:
            import torch.nn as nn  # noqa: F401 — imported for side effect of raising
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for quantizer:encoder", hint="pip install torch"
            ) from exc
        self.inputdim = inputdim
        self.hiddendim = hiddendim
        self.net = nn.Sequential(nn.Linear(inputdim, hiddendim), nn.ReLU())

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode ``x`` to the hidden representation.

        Args:
            x: ``[batch, inputdim]`` tensor.

        Returns:
            ``[batch, hiddendim]`` tensor.
        """
        return torch.relu(self.net[0](x))

    def parameters(self) -> Any:
        """Return trainable parameters."""
        return self.net.parameters()

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
