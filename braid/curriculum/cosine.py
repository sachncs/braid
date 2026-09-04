"""Cosine difficulty ramp curriculum."""

from __future__ import annotations

import math
from typing import Any

from braid.core.registry import registry


@registry.register(category="curriculum", name="cosine")
class cosine:
    """Difficulty follows a cosine curve from 0 to 1 over ``maxsteps``.

    Attributes:
        maxsteps: total step count.
    """

    name: str = "cosine"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, maxsteps: int) -> None:
        if maxsteps <= 0:
            raise ValueError("maxsteps must be > 0")
        self.maxsteps = maxsteps

    def difficulty(self, step: int) -> float:
        """Return current difficulty in [0, 1].

        Args:
            step: current training step.

        Returns:
            Float in ``[0, 1]``.
        """
        progress = min(1.0, max(0.0, step / self.maxsteps))
        return 0.5 * (1 - math.cos(math.pi * progress))

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.curriculum.cosine.difficulty", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
