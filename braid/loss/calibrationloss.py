"""Calibration loss — Expected Calibration Error."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="loss", name="calibrationloss")
class calibrationloss:
    """Approximate calibration loss via binned KL."""

    name: str = "calibrationloss"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, nbins: int = 10) -> None:
        self.nbins = nbins

    def compute(self, scores: Any, labels: Any, weight: float = 1.0) -> Any:
        try:
            import torch
            import torch.nn.functional as F
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("pytorch required for calibrationloss") from exc
        probs = F.softmax(scores, dim=-1)
        confidences, predictions = probs.max(dim=-1)
        accuracies = predictions.eq(labels).float()
        bins = torch.linspace(0, 1, self.nbins + 1, device=scores.device)
        ece = probs.new_zeros(())
        for i in range(self.nbins):
            mask = (confidences > bins[i]) & (confidences <= bins[i + 1])
            if mask.any():
                ece = ece + (accuracies[mask].mean() - confidences[mask].mean()).abs() * mask.float().mean()
        return weight * ece

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.loss.calibration.ece", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
