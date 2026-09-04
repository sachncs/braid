"""Reward-proxy training phase.

Trains the long-term-return reward MLP. Real implementation arrives in O3.
"""

from __future__ import annotations

from typing import Any

from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="phase", name="reward")
class reward:
    """Reward-proxy training phase.

    Attributes:
        horizon: prediction horizon (days) for the proxy.
        maxsteps: training steps.
    """

    name: str = "reward"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, horizon: int = 30, maxsteps: int = 1000) -> None:
        """Initialize the reward phase.

        Args:
            horizon: prediction horizon in days. Defaults to 30.
            maxsteps: training steps. Defaults to 1000.
        """
        self.horizon = horizon
        self.maxsteps = maxsteps

    def setup(self) -> None:
        return None

    def run(self) -> dict[str, Any]:
        log = getlogger("braid.phase.reward")
        log.info("reward.start", horizon=self.horizon, steps=self.maxsteps)
        return {"phase": "reward", "steps": self.maxsteps, "artifact": "rewardproxy.pt"}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
