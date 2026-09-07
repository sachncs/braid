"""Fallback-to-baseline drift response.

Toggles a fallback flag when drift is detected. Single-word naming.
"""

from __future__ import annotations

from typing import Any

from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="driftresponse", name="fallback")
class fallback:
    """Toggles ``usingbaseline`` when drift is detected.

    Attributes:
        usingbaseline: ``True`` after a drift signal is responded to.
    """

    name: str = "fallback"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self) -> None:
        self.usingbaseline = False

    def respond(self, signal: dict[str, Any]) -> None:
        """Toggle the fallback flag and log the activation.

        Args:
            signal: a drift signal dict.
        """
        self.usingbaseline = True
        getlogger("braid.driftresponse.fallback").warning(
            "baseline.fallback.active", score=signal.get("score")
        )

    def reset(self) -> None:
        """Reset ``usingbaseline`` to False."""
        self.usingbaseline = False

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
