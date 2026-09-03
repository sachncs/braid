"""Token dropout regularizer."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="regularizer", name="tokendropout")
class tokendropout:
    """Random token-level dropout on input ids."""

    name: str = "tokendropout"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, p: float = 0.1, replacetoken: int = 0) -> None:
        if not 0 <= p < 1:
            raise ValueError("p must be in [0, 1)")
        self.p = p
        self.replacetoken = replacetoken

    def apply(self, inputids: Any) -> Any:
        """Drop tokens with probability ``p``."""
        try:
            import torch
        except ImportError:
            return inputids
        mask = torch.rand_like(inputids.float()) < self.p
        out = inputids.clone()
        out[mask] = self.replacetoken
        return out

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
