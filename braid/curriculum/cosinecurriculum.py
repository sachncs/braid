"""Cosine difficulty ramp."""

from __future__ import annotations

import math
from typing import Any

from braid.core.registry import registry


@registry.register(category="curriculum", name="cosinecurriculum")
class cosinecurriculum:
    """Difficulty grows following a cosine curve."""

    name: str = "cosinecurriculum"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, maxsteps: int) -> None:
        self.maxsteps = maxsteps

    def difficulty(self, step: int) -> float:
        progress = min(1.0, max(0.0, step / max(1, self.maxsteps)))
        return 0.5 * (1 - math.cos(math.pi * progress))

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
