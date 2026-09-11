"""Alert-only drift response."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.core.logging import getlogger


@registry.register(category="driftresponse", name="alert")
class alert:
    """Log a structured warning when drift is detected."""

    name: str = "alert"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, channel: str = "braid.drift") -> None:
        self.channel = channel
        self.log = getlogger(channel)

    def respond(self, signal: dict[str, Any]) -> None:
        """Emit an alert for a drift signal."""
        self.log.warning(
            "drift.detected", score=signal.get("score"), detector=signal.get("detector")
        )

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.driftresponse.alerts", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
