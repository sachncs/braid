"""Reward-proxy training phase."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="phase", name="rewardproxyphase")
class rewardproxyphase:
    """Train the long-term-return proxy model."""

    name: str = "rewardproxyphase"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, horizon: int = 30, maxsteps: int = 1000) -> None:
        self.horizon = horizon
        self.maxsteps = maxsteps

    def setup(self) -> None:
        return None

    def run(self) -> dict[str, Any]:
        from braid.core.logging import getlogger

        log = getlogger("braid.phase.rewardproxyphase")
        log.info("rewardproxy.start", horizon=self.horizon, steps=self.maxsteps)
        log.info("rewardproxy.complete")
        return {"phase": "rewardproxy", "steps": self.maxsteps, "artifact": "rewardproxy.pt"}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
