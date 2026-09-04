"""Phase-2 post-training runner for ranking with the braided loss.

Real implementation arrives in O2.
"""

from __future__ import annotations

from typing import Any

from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="phase", name="postrain")
class postrain:
    """Phase-2 ranking training using the braided loss.

    Attributes:
        maxsteps: training steps.
        braidterms: list of (lossname, weight) pairs.
    """

    name: str = "postrain"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(
        self,
        maxsteps: int = 8000,
        braidterms: list[tuple[str, float]] | None = None,
    ) -> None:
        """Initialize postrain.

        Args:
            maxsteps: training steps. Defaults to 8000.
            braidterms: list of (lossname, weight). Defaults to a reasonable braid.
        """
        self.maxsteps = maxsteps
        self.braidterms = braidterms or [
            ("rankingce", 1.0),
            ("rewardweighted", 0.5),
            ("diversityentropy", 0.05),
        ]

    def setup(self) -> None:
        return None

    def run(self) -> dict[str, Any]:
        log = getlogger("braid.phase.postrain")
        log.info("postrain.start", steps=self.maxsteps, braidterms=self.braidterms)
        return {"phase": "postrain", "steps": self.maxsteps, "artifact": "postrain.safetensors"}

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.phase.postrain.step", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
