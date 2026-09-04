"""RQ-VAE decoder."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="quantizer", name="decoder")
class decoder:
    """Tiny decoder stub."""

    name: str = "decoder"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})  # not async-capable

    def __init__(self, hiddendim: int = 128, outputdim: int = 64) -> None:
        self.hiddendim = hiddendim
        self.outputdim = outputdim
        self.w: np.ndarray | None = None

    def fit(self, x: np.ndarray) -> None:
        rng = np.random.default_rng(0)
        self.w = rng.standard_normal((self.hiddendim, self.outputdim)).astype(np.float32) * 0.05

    def decode(self, z: np.ndarray) -> np.ndarray:
        if self.w is None:
            self.fit(np.zeros((1, self.hiddendim), dtype=np.float32))
        return z @ self.w

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
