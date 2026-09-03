"""Linear difficulty ramp."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="curriculum", name="linearcurriculum")
class linearcurriculum:
    """Difficulty grows linearly from 0..1 over ``maxsteps``."""

    name: str = "linearcurriculum"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, maxsteps: int) -> None:
        self.maxsteps = maxsteps

    def difficulty(self, step: int) -> float:
        return min(1.0, max(0.0, step / max(1, self.maxsteps)))

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
