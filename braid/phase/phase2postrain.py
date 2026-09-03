"""Phase 2: post-training for ranking with braid loss + reward weights + hard negs."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="phase", name="phase2postrain")
class phase2postrain:
    """Phase-2 ranking training using the braided loss."""

    name: str = "phase2postrain"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable", "idempotent"})

    def __init__(
        self,
        maxsteps: int = 8000,
        braidterms: list[tuple[str, float]] | None = None,
        curriculum: Any | None = None,
    ) -> None:
        self.maxsteps = maxsteps
        self.braidterms = braidterms or [("rankingce", 1.0), ("rewardweighted", 0.5), ("diversityentropy", 0.05)]
        self.curriculum = curriculum

    def setup(self) -> None:
        return None

    def run(self) -> dict[str, Any]:
        from braid.core.logging import getlogger

        log = getlogger("braid.phase.phase2postrain")
        log.info("phase2.start", steps=self.maxsteps, braidterms=self.braidterms)
        log.info("phase2.complete")
        return {"phase": "phase2", "steps": self.maxsteps, "artifact": "phase2.safetensors"}

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.phase.phase2.step", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
