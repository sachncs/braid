"""Down-scale a config for fast tests.

Walks a Pydantic config object and shrinks numeric fields, history
lengths, batch sizes, and embedding dims.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class scaledown:
    """Produce a scaled-down copy of a config for testing.

    Example:
        >>> cfg = ...
        >>> small = scaledown(cfg).run()
    """

    cfg: Any
    catalogmax: int = 1000
    historymax: int = 10
    batchsize: int = 4
    maxsteps: int = 50
    embeddingdim: int = 64
    nusers: int = 100
    seed: int = 0

    def run(self) -> Any:
        """Return a shallow copy with down-scaled numeric values.

        Returns:
            A new config instance with the same type as ``self.cfg``.
        """
        import copy

        out = copy.deepcopy(self.cfg)
        for attr in vars(out):
            if attr in {
                "catalogmax",
                "historymax",
                "batchsize",
                "maxsteps",
                "embeddingdim",
                "nusers",
                "seed",
            }:
                setattr(out, attr, getattr(self, attr))
        return out
