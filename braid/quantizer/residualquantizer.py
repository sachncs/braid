"""Residual quantizer (RQ-VAE codebook)."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="rqvae", name="residualquantizer")
class residualquantizer:
    """Residual VQ-VAE codebook."""

    name: str = "residualquantizer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, numcodes: int = 256, dim: int = 64, numstages: int = 4, seed: int = 0) -> None:
        self.numcodes = numcodes
        self.dim = dim
        self.numstages = numstages
        rng = np.random.default_rng(seed)
        self.codebooks = [rng.standard_normal((numcodes, dim)).astype(np.float32) for _ in range(numstages)]

    def quantize(self, vector: np.ndarray) -> list[int]:
        """Map a vector to a list of code indices via residual quantization."""
        codes: list[int] = []
        residual = vector.copy().astype(np.float32)
        for cb in self.codebooks:
            sims = cb @ residual
            codes.append(int(np.argmax(sims)))
            residual = residual - cb[codes[-1]]
        return codes

    def dequantize(self, codes: list[int]) -> np.ndarray:
        """Reconstruct a vector from a code sequence."""
        out = np.zeros(self.dim, dtype=np.float32)
        for cb, c in zip(self.codebooks, codes):
            out = out + cb[c]
        return out

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
