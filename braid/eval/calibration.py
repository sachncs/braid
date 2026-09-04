"""Calibration evaluator (ECE, brier, NLL, reliability diagram).

Computes expected calibration error (ECE), Brier score, negative log-likelihood
and a reliability table for downstream plotting.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="eval", name="calibration")
class calibration:
    """Expected Calibration Error (ECE), Brier and reliability stats."""

    name: str = "calibration"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, nbins: int = 10) -> None:
        self.nbins = nbins

    def evaluate(self, scores: list[float], labels: list[int]) -> dict[str, Any]:
        """Return ECE, brier, nll and per-bin reliability.

        Args:
            scores: predicted probability of the positive class in [0, 1].
            labels: ground-truth binary labels (0/1).

        Returns:
            A dict with ``ece``, ``brier``, ``nll`` and ``bins``.
        """
        if not scores:
            return {"ece": 0.0, "brier": 0.0, "nll": 0.0, "bins": []}
        if len(scores) != len(labels):
            raise ValueError(f"scores ({len(scores)}) and labels ({len(labels)}) must align")
        s = np.asarray(scores, dtype=np.float64)
        y = np.asarray(labels, dtype=np.float64)
        s = np.clip(s, 1e-7, 1.0 - 1e-7)
        bins = np.linspace(0, 1, self.nbins + 1)
        ece = 0.0
        out: list[dict[str, float]] = []
        for i in range(self.nbins):
            mask = (s >= bins[i]) & (s <= bins[i + 1])
            if mask.any():
                avgconf = float(s[mask].mean())
                avgacc = float(y[mask].mean())
                gap = abs(avgconf - avgacc)
                ece += gap * mask.mean()
                out.append(
                    {
                        "binlo": float(bins[i]),
                        "binhi": float(bins[i + 1]),
                        "conf": avgconf,
                        "acc": avgacc,
                        "gap": gap,
                        "count": int(mask.sum()),
                    }
                )
        brier = float(np.mean((s - y) ** 2))
        nll = float(-np.mean(y * np.log(s) + (1 - y) * np.log(1 - s)))
        return {"ece": float(ece), "brier": brier, "nll": nll, "bins": out}

    def observability(self) -> dict[str, Any]:
        return {
            "metrics": [
                {"name": "braid.eval.calibration.ece", "type": "gauge"},
                {"name": "braid.eval.calibration.brier", "type": "gauge"},
                {"name": "braid.eval.calibration.nll", "type": "gauge"},
            ]
        }

    def metrics(self) -> list[Any]:
        return []
