"""RQ-VAE encoder."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="rqvae", name="encoder")
class encoder:
    """Tiny encoder stub. Real impl: a small conv/MLP."""

    name: str = "encoder"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, inputdim: int = 64, hiddendim: int = 128) -> None:
        self.inputdim = inputdim
        self.hiddendim = hiddendim
        self._w: np.ndarray | None = None

    def fit(self, x: np.ndarray) -> None:
        rng = np.random.default_rng(0)
        self._w = rng.standard_normal((self.inputdim, self.hiddendim)).astype(np.float32) * 0.05

    def encode(self, x: np.ndarray) -> np.ndarray:
        if self._w is None:
            self.fit(np.zeros((1, self.inputdim), dtype=np.float32))
        return np.maximum(0, x @ self._w) if x.ndim > 1 else np.maximum(0, x @ self._w)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
