"""Linear difficulty ramp curriculum."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="curriculum", name="linear")
class linear:
    """Difficulty grows linearly from 0 to 1 over ``maxsteps`` steps.

    Attributes:
        maxsteps: total step count over which difficulty reaches 1.
    """

    name: str = "linear"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, maxsteps: int) -> None:
        if maxsteps <= 0:
            raise ValueError("maxsteps must be > 0")
        self.maxsteps = maxsteps

    def difficulty(self, step: int) -> float:
        """Return current difficulty in [0, 1].

        Args:
            step: current training step (0-indexed).

        Returns:
            Float in ``[0, 1]``.
        """
        return min(1.0, max(0.0, step / self.maxsteps))

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.curriculum.linear.difficulty", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
