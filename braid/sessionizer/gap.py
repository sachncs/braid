"""Gap-based sessionizer.

Splits an event stream into sessions whenever the gap between consecutive
events exceeds a threshold.
"""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.registry import registry


@registry.register(category="sessionizer", name="gap")
class gapsessionizer:
    """Group events into sessions by max gap.

    Attributes:
        gapseconds: maximum idle time within a session.
    """

    name: str = "gap"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"streamable", "observable"})

    def __init__(self, gapseconds: int = 1800) -> None:
        """Initialize.

        Args:
            gapseconds: max gap (s) within a session. Defaults to 30 min.
        """
        self.gapseconds = gapseconds

    def sessionize(self, events: Iterable[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        """Split ``events`` into sessions.

        Args:
            events: events with a ``timestamp`` field.

        Returns:
            A list of sessions, each a list of events.
        """
        out: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        last_ts: float | None = None
        for e in sorted(events, key=lambda r: r.get("timestamp", 0)):
            ts = float(e.get("timestamp", 0))
            if last_ts is None or ts - last_ts <= self.gapseconds:
                current.append(e)
            else:
                if current:
                    out.append(current)
                current = [e]
            last_ts = ts
        if current:
            out.append(current)
        return out

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
