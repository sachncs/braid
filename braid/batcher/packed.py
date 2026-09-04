"""Packed (no padding) batcher.

Joins sequences end-to-end with attention masking at the join points.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="batcher", name="packed")
class packed:
    """Pack sequences into a single tensor up to ``maxtokens``.

    Attributes:
        maxtokens: hard cap on the number of tokens per packed output.
    """

    name: str = "packed"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, maxtokens: int = 8192) -> None:
        if maxtokens <= 0:
            raise ValueError("maxtokens must be > 0")
        self.maxtokens = maxtokens

    def batch(self, sequences: list[list[int]]) -> Any:
        """Pack a list of sequences end-to-end.

        Args:
            sequences: list of int sequences.

        Returns:
            Dict ``{"tokens": tensor-or-list, "offsets": positions}`` or
            the original list if torch is unavailable.
        """
        try:
            import torch

            flat: list[int] = []
            offsets: list[int] = [0]
            for seq in sequences:
                flat.extend(seq)
                offsets.append(len(flat))
            out = torch.tensor(flat[: self.maxtokens], dtype=torch.long)
            return {"tokens": out, "offsets": offsets}
        except ImportError:
            flat = [tok for seq in sequences for tok in seq]
            return {"tokens": flat[: self.maxtokens], "offsets": [0]}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
