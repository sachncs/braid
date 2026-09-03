"""Step curriculum.

Difficulty ramps in discrete steps.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="curriculum", name="stepcurriculum")
class stepcurriculum:
    """Step-like difficulty ramp."""

    name: str = "stepcurriculum"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, maxsteps: int, nsteps: int = 4) -> None:
        if nsteps <= 0:
            raise ValueError("nsteps must be > 0")
        self.maxsteps = maxsteps
        self.nsteps = nsteps

    def difficulty(self, step: int) -> float:
        progress = min(1.0, max(0.0, step / max(1, self.maxsteps)))
        level = int(progress * self.nsteps)
        return min(1.0, (level + 1) / self.nsteps)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
