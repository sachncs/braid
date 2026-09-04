"""Sorted-then-padded batcher."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.batcher.padded import padded as paddedconcrete


@registry.register(category="batcher", name="sorted")
class sorted:
    """Sort all sequences by length, then pad; simple and effective.

    Attributes:
        batchsize: target batch size.
        padtoken: id used for padding.
    """

    name: str = "sorted"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, batchsize: int, padtoken: int = 0) -> None:
        if batchsize <= 0:
            raise ValueError("batchsize must be > 0")
        self.batchsize = batchsize
        self.padtoken = padtoken

    def batch(self, sequences: list[list[int]]) -> list[Any]:
        """Sort all sequences by length (longest first), then pad each chunk.

        Args:
            sequences: list of int sequences.

        Returns:
            List of batched outputs.
        """
        sortedseqs = sorted(sequences, key=len, reverse=True)
        batches: list[Any] = []
        for i in range(0, len(sortedseqs), self.batchsize):
            chunk = sortedseqs[i : i + self.batchsize]
            batches.append(paddedconcrete(self.batchsize, self.padtoken).batch(chunk))
        return batches

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
