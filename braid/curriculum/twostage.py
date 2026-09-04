"""Two-stage curriculum: easy phase → hard phase."""

from __future__ import annotations

from typing import Any, Literal

from braid.core.registry import registry


@registry.register(category="curriculum", name="twostage")
class twostage:
    """Two-stage switch curriculum.

    Easy phase runs first, then ramp into hard phase at ``switchat``.

    Attributes:
        maxsteps: total steps.
        switchat: fraction of ``maxsteps`` at which to switch phases.
    """

    name: str = "twostage"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, maxsteps: int, switchat: float = 0.5) -> None:
        if maxsteps <= 0:
            raise ValueError("maxsteps must be > 0")
        if not 0 < switchat < 1:
            raise ValueError("switchat must be in (0, 1)")
        self.maxsteps = maxsteps
        self.switchat = switchat

    def difficulty(self, step: int) -> float:
        """Return current difficulty in [0, 1]."""
        progress = step / self.maxsteps
        if progress < self.switchat:
            return 0.2
        rem = (progress - self.switchat) / max(1e-9, 1 - self.switchat)
        return min(1.0, 0.2 + rem * 0.8)

    def phase(self, step: int) -> Literal["easy", "hard"]:
        """Return current phase as a string."""
        return "easy" if step / self.maxsteps < self.switchat else "hard"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
