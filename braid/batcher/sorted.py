"""Sorted-then-padded batcher."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="batcher", name="sortedpaddedbatcher")
class sortedpaddedbatcher:
    """Sort by length then pad; simple and effective."""

    name: str = "sortedpaddedbatcher"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, batchsize: int, padtoken: int = 0) -> None:
        self.batchsize = batchsize
        self.padtoken = padtoken

    def batch(self, sequences: list[list[int]]) -> list[Any]:
        from braid.batcher.paddedbatcher import paddedbatcher

        sortedseqs = sorted(sequences, key=len, reverse=True)
        batches: list[Any] = []
        for i in range(0, len(sortedseqs), self.batchsize):
            chunk = sortedseqs[i : i + self.batchsize]
            batches.append(paddedbatcher(self.batchsize, self.padtoken).batch(chunk))
        return batches

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
