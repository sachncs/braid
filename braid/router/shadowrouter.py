"""Shadow router — runs treatment in parallel, returns control."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="router", name="shadowrouter")
class shadowrouter:
    """Returns control response; runs treatment in shadow mode for offline analysis."""

    name: str = "shadowrouter"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "shadowmode", "lowlatency", "async"})

    def __init__(self, arms: list[str] | None = None) -> None:
        self.arms = arms or ["control", "treatment"]

    def route(self, key: str | None = None) -> str:
        return "control"

    def shadowroute(self, key: str | None = None) -> str:
        return self.arms[-1]

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
