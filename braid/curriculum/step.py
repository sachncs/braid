"""Step (piecewise) difficulty curriculum."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="curriculum", name="step")
class step:
    """Step-like difficulty ramp.

    Difficulty levels = ``(i+1) / nsteps`` for ``i in 0..nsteps-1``.

    Attributes:
        maxsteps: total step count.
        nsteps: number of discrete difficulty levels.
    """

    name: str = "step"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, maxsteps: int, nsteps: int = 4) -> None:
        if maxsteps <= 0:
            raise ValueError("maxsteps must be > 0")
        if nsteps <= 0:
            raise ValueError("nsteps must be > 0")
        self.maxsteps = maxsteps
        self.nsteps = nsteps

    def difficulty(self, step: int) -> float:
        """Return current difficulty in [0, 1]."""
        progress = min(1.0, max(0.0, step / self.maxsteps))
        level = int(progress * self.nsteps)
        return min(1.0, (level + 1) / self.nsteps)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
