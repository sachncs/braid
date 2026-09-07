"""Padded batcher — pads sequences to the longest in the batch."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="batcher", name="padded")
class padded:
    """Pad-to-max-length batcher.

    Attributes:
        batchsize: target batch size.
        padtoken: id used for padding.
    """

    name: str = "padded"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, batchsize: int, padtoken: int = 0) -> None:
        if batchsize <= 0:
            raise ValueError("batchsize must be > 0")
        self.batchsize = batchsize
        self.padtoken = padtoken

    def batch(self, sequences: list[list[int]]) -> Any:
        """Pad a list of sequences to max length and return a tensor (or lists).

        Args:
            sequences: list of int sequences.

        Returns:
            ``[batch, maxlen]`` int64 tensor (or 2D list if torch is unavailable).
        """
        try:
            import torch

            n = len(sequences)
            lmax = max(len(s) for s in sequences)
            out = torch.full((n, lmax), self.padtoken, dtype=torch.long)
            for i, s in enumerate(sequences):
                out[i, : len(s)] = torch.tensor(s, dtype=torch.long)
            return out
        except ImportError:
            lmax = max((len(s) for s in sequences), default=0)
            out = [[self.padtoken] * lmax for _ in sequences]
            for i, s in enumerate(sequences):
                for j, tok in enumerate(s):
                    out[i][j] = tok
            return out

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
