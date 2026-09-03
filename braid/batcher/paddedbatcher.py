"""Padded batcher."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="batcher", name="paddedbatcher")
class paddedbatcher:
    """Pad-to-max-length batcher."""

    name: str = "paddedbatcher"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, batchsize: int, padtoken: int = 0) -> None:
        self.batchsize = batchsize
        self.padtoken = padtoken

    def batch(self, sequences: list[list[int]]) -> Any:
        """Pad to max length."""
        try:
            import torch
        except ImportError:
            return sequences
        n = len(sequences)
        lmax = max(len(s) for s in sequences)
        out = torch.full((n, lmax), self.padtoken, dtype=torch.long)
        for i, s in enumerate(sequences):
            out[i, : len(s)] = torch.tensor(s, dtype=torch.long)
        return out

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
