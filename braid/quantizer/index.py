"""RQ-VAE semantic-ID index."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry
from braid.quantizer.quantizer import quantizer


@registry.register(category="rqvae", name="index")
class index:
    """Maps semantic IDs to item ids."""

    name: str = "index"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"shardedcatalog", "observable", "async"})

    def __init__(self, numcodes: int = 256, dim: int = 64, numstages: int = 4) -> None:
        self.quantizer = residualquantizer(numcodes=numcodes, dim=dim, numstages=numstages)
        self._tocluster: dict[tuple[int, ...], list[int]] = {}

    def add(self, itemid: int, codes: list[int]) -> None:
        key = tuple(codes)
        self._tocluster.setdefault(key, []).append(itemid)

    def find(self, codes: list[int]) -> list[int]:
        return self._tocluster.get(tuple(codes), [])

    def allitems(self) -> list[int]:
        out: list[int] = []
        for v in self._tocluster.values():
            out.extend(v)
        return sorted(out)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
