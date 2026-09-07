"""Jensen-Shannon Divergence drift detector."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="drift", name="jsd")
class jsd:
    """Jensen-Shannon divergence detector."""

    name: str = "jsd"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, threshold: float = 0.1) -> None:
        self.threshold = threshold
        self.reference: np.ndarray | None = None

    def setreference(self, ref: np.ndarray) -> None:
        self.reference = np.asarray(ref, dtype=np.float64)

    def update(self, dist: np.ndarray) -> dict[str, Any]:
        """Compute JSD between reference and the new distribution."""
        if self.reference is None:
            return {"score": 0.0, "drifted": False}
        a = np.asarray(self.reference, dtype=np.float64)
        b = np.asarray(dist, dtype=np.float64)
        n = min(len(a), len(b))
        a = a[:n] + 1e-12
        b = b[:n] + 1e-12
        a = a / a.sum()
        b = b / b.sum()
        m = 0.5 * (a + b)
        kl_am = np.sum(a * np.log(a / m))
        kl_bm = np.sum(b * np.log(b / m))
        score = float(0.5 * (kl_am + kl_bm))
        return {"score": score, "drifted": score > self.threshold}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
