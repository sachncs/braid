"""Calibration evaluator (ECE)."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="eval", name="calibration")
class calibration:
    """Expected Calibration Error evaluator."""

    name: str = "calibration"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, nbins: int = 10) -> None:
        self.nbins = nbins

    def evaluate(self, scores: list[float], labels: list[int]) -> dict[str, float]:
        """Return ECE and binned reliability stats."""
        if not scores:
            return {"ece": 0.0, "bins": []}
        s = np.asarray(scores)
        y = np.asarray(labels)
        bins = np.linspace(0, 1, self.nbins + 1)
        ece = 0.0
        out: list[dict[str, float]] = []
        for i in range(self.nbins):
            mask = (s > bins[i]) & (s <= bins[i + 1])
            if mask.any():
                avgconf = float(s[mask].mean())
                avgacc = float(y[mask].mean())
                gap = abs(avgconf - avgacc)
                ece += gap * mask.mean()
                out.append({"binlo": float(bins[i]), "binhi": float(bins[i + 1]), "conf": avgconf, "acc": avgacc, "gap": gap})
        return {"ece": float(ece), "bins": out}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
