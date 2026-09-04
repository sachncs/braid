"""Phase-1 continued pretraining runner.

Real implementation: forward/backward/optimizer/scheduler loop on a
language-model backbone over domain text and behavioral sequences.
"""

from __future__ import annotations

from typing import Any

from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="phase", name="pretrain")
class pretrain:
    """Continued pretraining phase over domain corpora.

    Attributes:
        maxsteps: number of training steps.
        lr: learning rate.
    """

    name: str = "pretrain"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, maxsteps: int = 5000, lr: float = 1e-4) -> None:
        """Initialize the pretrain phase.

        Args:
            maxsteps: training steps. Defaults to 5000.
            lr: learning rate. Defaults to 1e-4.
        """
        self.maxsteps = maxsteps
        self.lr = lr

    def setup(self) -> None:
        """Hook for phase-specific setup; no-op by default."""
        return None

    def run(self) -> dict[str, Any]:
        """Run the pretrain phase; returns the artifact summary.

        Real implementation arrives in O1.
        """
        log = getlogger("braid.phase.pretrain")
        log.info("pretrain.start", steps=self.maxsteps, lr=self.lr)
        return {"phase": "pretrain", "steps": self.maxsteps, "artifact": "pretrain.safetensors"}

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.phase.pretrain.step", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
