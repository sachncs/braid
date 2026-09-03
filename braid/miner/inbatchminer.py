"""In-batch negative miner."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="miner", name="inbatchminer")
class inbatchminer:
    """Treat every other item in the batch as a negative."""

    name: str = "inbatchminer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def mine(self, positives: Any, scoresfn: Any | None = None) -> Any:
        try:
            import torch
        except ImportError:
            return []
        n = positives.shape[0] if hasattr(positives, "shape") else len(positives)
        idx = torch.arange(n).unsqueeze(0).repeat(n, 1)
        mask = idx != torch.arange(n).unsqueeze(1)
        return idx[mask].reshape(n, n - 1)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
