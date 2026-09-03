"""Fallback-to-baseline drift response."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.core.logging import getlogger


@registry.register(category="driftresponse", name="fallbackbaseline")
class fallbackbaseline:
    """Toggles a fallback flag when drift is detected."""

    name: str = "fallbackbaseline"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self) -> None:
        self.usingbaseline = False

    def respond(self, signal: dict[str, Any]) -> None:
        self.usingbaseline = True
        getlogger("braid.driftresponse.fallbackbaseline").warning(
            "baseline.fallback.active", score=signal.get("score")
        )

    def reset(self) -> None:
        self.usingbaseline = False

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
