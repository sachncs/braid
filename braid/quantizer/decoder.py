"""Quantizer decoder — trainable MLP projecting back from the latent."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="quantizer", name="decoder")
class decoder:
    """Trainable MLP decoder.

    Projects ``[batch, hiddendim]`` → ``[batch, outputdim]``.
    """

    name: str = "decoder"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, hiddendim: int = 128, outputdim: int = 64) -> None:
        try:
            import torch
            import torch.nn as nn
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for quantizer:decoder", hint="pip install torch"
            ) from exc
        if hiddendim <= 0 or outputdim <= 0:
            raise ValueError("dims must be > 0")
        self.hiddendim = hiddendim
        self.outputdim = outputdim
        self.net = nn.Linear(hiddendim, outputdim)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent ``z`` to the output reconstruction.

        Args:
            z: ``[batch, hiddendim]`` tensor.

        Returns:
            ``[batch, outputdim]`` tensor.
        """
        return self.net(z)

    def parameters(self) -> Any:
        """Return trainable parameters."""
        return self.net.parameters()

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
