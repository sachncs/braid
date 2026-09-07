"""Random A/B router."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="router", name="randomrouter")
class randomrouter:
    """Random uniform A/B router."""

    name: str = "randomrouter"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency", "async"})

    def __init__(self, arms: list[str] | None = None, seed: int = 0) -> None:
        self.arms = arms or ["control", "treatment"]
        self.rng = __import__("random").Random(seed)

    def route(self, key: str | None = None) -> str:
        """Pick an arm uniformly."""
        return self.rng.choice(self.arms)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
