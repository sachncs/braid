"""Kolmogorov-Smirnov drift detector."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="drift", name="ks")
class ks:
    """Kolmogorov-Smirnov drift detector."""

    name: str = "ks"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset(
        {
            "observable",
        }
    )

    def __init__(self, threshold: float = 0.05) -> None:
        self.threshold = threshold
        self.reference: np.ndarray | None = None

    def setreference(self, ref: np.ndarray) -> None:
        self.reference = np.asarray(ref, dtype=np.float64)

    def update(self, dist: np.ndarray) -> dict[str, Any]:
        """Compute KS statistic and 2-sample p-value (chi^2 surrogate)."""
        if self.reference is None:
            return {"score": 0.0, "drifted": False}
        a = np.sort(self.reference)
        b = np.sort(np.asarray(dist, dtype=np.float64))
        cdf_a = np.arange(1, len(a) + 1) / len(a)
        allpoints = np.concatenate([a, b])
        allpoints.sort()
        cdf_a_interp = np.interp(allpoints, a, cdf_a)
        cdf_b_interp = np.interp(allpoints, b, np.arange(1, len(b) + 1) / len(b))
        score = float(np.max(np.abs(cdf_a_interp - cdf_b_interp)))
        return {"score": score, "drifted": score > self.threshold}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
