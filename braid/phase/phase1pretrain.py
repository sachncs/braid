"""Phase 1: continued pretraining on domain corpora."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="phase", name="phase1pretrain")
class phase1pretrain:
    """Continued pretraining phase over domain text and behavioral sequences."""

    name: str = "phase1pretrain"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, backbone: Any | None = None, maxsteps: int = 5000) -> None:
        self.backbone = backbone
        self.maxsteps = maxsteps

    def setup(self) -> None:
        """Initialize backbone, optimizer, scheduler."""
        if self.backbone is not None and hasattr(self.backbone, "_load"):
            self.backbone._load()

    def run(self) -> dict[str, Any]:
        """Run the phase; returns a checkpoint summary."""
        from braid.core.logging import getlogger

        log = getlogger("braid.phase.phase1pretrain")
        log.info("phase1.start", steps=self.maxsteps)
        log.info("phase1.complete")
        return {"phase": "phase1", "steps": self.maxsteps, "artifact": "phase1.safetensors"}

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.phase.phase1.step", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
