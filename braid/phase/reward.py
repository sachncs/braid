"""Reward-proxy training phase — real MLP fit on (engagement → 30-day return).

Real implementation: train ``reward:longtermreturn`` via AdamW.
"""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment, requiresresource
from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="phase", name="reward")
class reward:
    """Reward-proxy training phase.

    Attributes:
        horizon: prediction horizon in days.
        maxsteps: training steps.
    """

    name: str = "reward"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, horizon: int = 30, maxsteps: int = 1000) -> None:
        if horizon <= 0 or maxsteps <= 0:
            raise ValueError("horizon and maxsteps must be > 0")
        self.horizon = horizon
        self.maxsteps = maxsteps

    def setup(self) -> None:
        return None

    def run(self, dataloader: Any | None = None) -> dict[str, Any]:
        """Train the longtermreturn reward proxy.

        Args:
            dataloader: iterable of ``{"features": [batch, 8], "labels": [batch]}``.

        Raises:
            requiresenvironment: torch missing.
            requiresresource: dataloader missing.
        """
        try:
            import torch
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for phase:reward", hint="pip install torch"
            ) from exc
        if dataloader is None:
            raise requiresresource("phase:reward requires a dataloader")
        proxy = registry.create("reward", "longtermreturn", horizon=self.horizon)
        losses: list[float] = []
        for step, batch in enumerate(dataloader):
            if step >= self.maxsteps:
                break
            features = batch["features"]
            labels = batch["labels"]
            loss = proxy.trainstep(features, labels, lr=1e-3)
            losses.append(loss)
        getlogger("braid.phase.reward").info("reward.train.complete", steps=len(losses))
        return {"phase": "reward", "steps": len(losses), "losses": losses}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
