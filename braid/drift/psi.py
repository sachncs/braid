"""PSI (Population Stability Index) detector."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="drift", name="psi")
class psi:
    """PSI drift detector."""

    name: str = "psi"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset(
        {
            "observable",
        }
    )

    def __init__(self, nbins: int = 10, threshold: float = 0.2) -> None:
        self.nbins = nbins
        self.threshold = threshold
        self.reference: np.ndarray | None = None

    def setreference(self, ref: np.ndarray) -> None:
        """Set the reference distribution."""
        self.reference = np.asarray(ref, dtype=np.float64)

    def update(self, dist: np.ndarray) -> dict[str, Any]:
        """Compute PSI between ``dist`` and the reference.

        Args:
            dist: a recent distribution.

        Returns:
            A dict with ``score`` and ``drifted``.
        """
        if self.reference is None:
            return {"score": 0.0, "drifted": False}
        a = np.asarray(self.reference, dtype=np.float64)
        b = np.asarray(dist, dtype=np.float64)
        # Resample if sizes differ.
        n = min(len(a), len(b))
        a = a[:n]
        b = b[:n]
        a = a / max(a.sum(), 1e-8)
        b = b / max(b.sum(), 1e-8)
        score = float(np.sum((b - a) * np.log((b + 1e-8) / (a + 1e-8))))
        return {"score": score, "drifted": score > self.threshold}

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.drift.psi.score", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
