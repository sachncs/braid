"""Length-bucketed batcher — sort by length within length bucket."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.batcher.padded import padded as paddedconcrete


@registry.register(category="batcher", name="bucket")
class bucket:
    """Bucket by length; reduces padding waste.

    Attributes:
        batchsize: target batch size.
        nbuckets: number of length buckets.
        padtoken: id used for padding.
    """

    name: str = "bucket"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, batchsize: int, nbuckets: int = 8, padtoken: int = 0) -> None:
        if batchsize <= 0:
            raise ValueError("batchsize must be > 0")
        if nbuckets <= 0:
            raise ValueError("nbuckets must be > 0")
        self.batchsize = batchsize
        self.nbuckets = nbuckets
        self.padtoken = padtoken

    def batch(self, sequences: list[list[int]]) -> list[Any]:
        """Bucket, sort each bucket by length, then pad.

        Args:
            sequences: list of int sequences.

        Returns:
            List of batched outputs (one per bucket).
        """
        sortedseqs = sorted(sequences, key=len)
        batches: list[Any] = []
        for i in range(0, len(sortedseqs), self.batchsize):
            chunk = sortedseqs[i : i + self.batchsize]
            batches.append(paddedconcrete(self.batchsize, self.padtoken).batch(chunk))
        return batches

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
