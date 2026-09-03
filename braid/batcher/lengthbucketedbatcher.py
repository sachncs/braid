"""Length-bucketed batcher (sort by length within bucket)."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="batcher", name="lengthbucketedbatcher")
class lengthbucketedbatcher:
    """Bucket by length; reduces padding waste."""

    name: str = "lengthbucketedbatcher"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, batchsize: int, nbuckets: int = 8, padtoken: int = 0) -> None:
        self.batchsize = batchsize
        self.nbuckets = nbuckets
        self.padtoken = padtoken

    def batch(self, sequences: list[list[int]]) -> list[Any]:
        """Return a list of batches sorted by length within each bucket."""
        from braid.batcher.paddedbatcher import paddedbatcher

        sortedseqs = sorted(sequences, key=len)
        batches: list[Any] = []
        for i in range(0, len(sortedseqs), self.batchsize):
            chunk = sortedseqs[i : i + self.batchsize]
            batches.append(paddedbatcher(self.batchsize, self.padtoken).batch(chunk))
        return batches

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
