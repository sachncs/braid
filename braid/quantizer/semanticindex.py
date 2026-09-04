"""Quantizer semantic-ID index.

Maps sets of semantic codes (one sequence per item) to item ids and
supports nearest-neighbor lookup by code prefix.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry
from braid.quantizer.quantizer import quantizer as quantizerconcrete


@registry.register(category="quantizer", name="semanticindex")
class semanticindex:
    """Maps semantic codes to item ids and supports prefix-based lookup.

    Attributes:
        numcodes: codes per stage.
        dim: latent dimension.
        numstages: number of residual stages.
    """

    name: str = "semanticindex"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"shardedcatalog", "observable", "async"})

    def __init__(self, numcodes: int = 256, dim: int = 64, numstages: int = 4) -> None:
        """Initialize the semantic index.

        Args:
            numcodes: codes per stage. Defaults to 256.
            dim: latent dimension. Defaults to 64.
            numstages: number of stages. Defaults to 4.
        """
        self._q: quantizerconcrete = quantizerconcrete(numcodes=numcodes, dim=dim, numstages=numstages)
        self._tocluster: dict[tuple[int, ...], list[int]] = {}

    def add(self, itemid: int, codes: list[int]) -> None:
        """Associate ``itemid`` with the given semantic code sequence.

        Args:
            itemid: item id.
            codes: list of codes (length ``numstages``).
        """
        key = tuple(codes)
        self._tocluster.setdefault(key, []).append(itemid)

    def find(self, codes: list[int]) -> list[int]:
        """Return items whose semantic codes match exactly.

        Args:
            codes: list of codes to look up.

        Returns:
            List of item ids (empty if none).
        """
        return self._tocluster.get(tuple(codes), [])

    def findprefix(self, codes: list[int], prefixlen: int = 1) -> list[int]:
        """Return items whose first ``prefixlen`` codes match ``codes``.

        Args:
            codes: query codes.
            prefixlen: how many leading codes must match.

        Returns:
            List of item ids whose prefix matches.
        """
        out: list[int] = []
        for k, items in self._tocluster.items():
            if len(k) >= prefixlen and k[:prefixlen] == tuple(codes[:prefixlen]):
                out.extend(items)
        return out

    def allitems(self) -> list[int]:
        """Return all indexed item ids sorted ascending."""
        out: list[int] = []
        for v in self._tocluster.values():
            out.extend(v)
        return sorted(out)

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.quantizer.semanticindex.size", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
