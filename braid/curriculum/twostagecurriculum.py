"""Two-stage curriculum.

Easy phase followed by hard phase with explicit switching.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="curriculum", name="twostagecurriculum")
class twostagecurriculum:
    """Easy→hard switching at ``switchat``."""

    name: str = "twostagecurriculum"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, maxsteps: int, switchat: float = 0.5) -> None:
        if not 0 < switchat < 1:
            raise ValueError("switchat must be in (0, 1)")
        self.maxsteps = maxsteps
        self.switchat = switchat

    def difficulty(self, step: int) -> float:
        progress = step / max(1, self.maxsteps)
        if progress < self.switchat:
            return 0.2
        rem = (progress - self.switchat) / max(1e-9, 1 - self.switchat)
        return min(1.0, 0.2 + rem * 0.8)

    def phase(self, step: int) -> str:
        return "easy" if step / max(1, self.maxsteps) < self.switchat else "hard"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
