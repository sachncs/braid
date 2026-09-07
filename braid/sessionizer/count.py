"""Count-based sessionizer.

Groups every N events into a session regardless of time.
"""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.registry import registry


@registry.register(category="sessionizer", name="count")
class countsessionizer:
    """Group every ``size`` events into a session.

    Attributes:
        size: number of events per session.
    """

    name: str = "count"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"streamable", "observable"})

    def __init__(self, size: int = 20) -> None:
        """Initialize.

        Args:
            size: events per session.
        """
        if size <= 0:
            raise ValueError("size must be > 0")
        self.size = size

    def sessionize(self, events: Iterable[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        """Group events into fixed-size sessions.

        Args:
            events: events to group.

        Returns:
            Sessions, each a list of size ``self.size`` (last may be shorter).
        """
        out: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        for e in events:
            current.append(e)
            if len(current) >= self.size:
                out.append(current)
                current = []
        if current:
            out.append(current)
        return out

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
