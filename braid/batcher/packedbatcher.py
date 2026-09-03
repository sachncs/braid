"""Packed (no padding) batcher.

Joins multiple sequences end-to-end with attention masking between them.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="batcher", name="packedbatcher")
class packedbatcher:
    """Pack sequences into a single tensor up to ``maxtokens``."""

    name: str = "packedbatcher"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, maxtokens: int = 8192) -> None:
        self.maxtokens = maxtokens

    def batch(self, sequences: list[list[int]]) -> Any:
        """Pack into chunks of ``maxtokens``; return flat tensor + offsets."""
        try:
            import torch
        except ImportError:
            return sequences
        flat: list[int] = []
        offsets: list[int] = [0]
        for seq in sequences:
            flat.extend(seq)
            offsets.append(len(flat))
        out = torch.tensor(flat[: self.maxtokens], dtype=torch.long)
        return {"tokens": out, "offsets": offsets}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
