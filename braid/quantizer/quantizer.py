"""Residual vector quantizer (RVQ).

Quantizes a vector into a sequence of code indices via residual
quantization. Concatenates multiple codebook stages, each operating
on the residual left after the previous stage.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="quantizer", name="quantizer")
class quantizer:
    """Residual vector quantizer.

    Attributes:
        numcodes: codes per stage.
        dim: latent dimension.
        numstages: number of residual stages.
        seed: RNG seed used at construction.
    """

    name: str = "quantizer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, numcodes: int = 256, dim: int = 64, numstages: int = 4, seed: int = 0) -> None:
        """Initialize the residual quantizer.

        Args:
            numcodes: codes per codebook stage. Defaults to 256.
            dim: latent dimension. Defaults to 64.
            numstages: number of residual stages. Defaults to 4.
            seed: RNG seed. Defaults to 0.
        """
        if numcodes <= 0:
            raise ValueError("numcodes must be > 0")
        if dim <= 0:
            raise ValueError("dim must be > 0")
        if numstages <= 0:
            raise ValueError("numstages must be > 0")
        self.numcodes = numcodes
        self.dim = dim
        self.numstages = numstages
        rng = np.random.default_rng(seed)
        self.codebooks: list[np.ndarray] = [rng.standard_normal((numcodes, dim)).astype(np.float32) for _ in range(numstages)]

    def quantize(self, vector: np.ndarray) -> list[int]:
        """Map a single vector to a list of code indices (one per stage).

        Args:
            vector: ``[dim]`` float array.

        Returns:
            A list of length ``numstages`` of int code indices.
        """
        codes: list[int] = []
        residual = vector.astype(np.float32).copy()
        for cb in self.codebooks:
            sims = cb @ residual
            codes.append(int(np.argmax(sims)))
            residual = residual - cb[codes[-1]]
        return codes

    def dequantize(self, codes: list[int]) -> np.ndarray:
        """Reconstruct the vector from a code sequence.

        Args:
            codes: list of stage indices (length ``numstages``).

        Returns:
            ``[dim]`` reconstructed vector.
        """
        if len(codes) != self.numstages:
            raise ValueError(f"expected {self.numstages} codes, got {len(codes)}")
        out = np.zeros(self.dim, dtype=np.float32)
        for cb, c in zip(self.codebooks, codes):
            out = out + cb[c]
        return out

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        """Return an idempotency key for cached construction."""
        return f"quantizer:{self.numcodes}:{self.dim}:{self.numstages}"

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.quantizer.quantize.calls", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
