"""Time-window sessionizer.

Splits events into sessions of fixed wall-clock duration.
"""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.registry import registry


@registry.register(category="sessionizer", name="timewindow")
class timewindowsessionizer:
    """Group events into fixed-duration windows.

    Attributes:
        windowseconds: length of each window.
    """

    name: str = "timewindow"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"streamable", "observable"})

    def __init__(self, windowseconds: int = 3600) -> None:
        """Initialize.

        Args:
            windowseconds: window duration (s).
        """
        self.windowseconds = windowseconds

    def sessionize(self, events: Iterable[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        """Split ``events`` into windows.

        Args:
            events: events with a ``timestamp`` field.

        Returns:
            List of sessions.
        """
        out: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        anchor: float | None = None
        for e in sorted(events, key=lambda r: r.get("timestamp", 0)):
            ts = float(e.get("timestamp", 0))
            if anchor is None:
                anchor = ts
            if ts - anchor > self.windowseconds:
                if current:
                    out.append(current)
                current = [e]
                anchor = ts
            else:
                current.append(e)
        if current:
            out.append(current)
        return out

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
