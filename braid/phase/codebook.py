"""Codebook (RVQ encoder+decoder+quantizer) training phase.

Real implementation: delegate to ``quantizer:trainer``.
"""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresresource
from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="phase", name="codebook")
class codebook:
    """Codebook training phase.

    Attributes:
        numcodes: codes per stage.
        codebooksize: alias of numcodes.
        maxsteps: training steps.
    """

    name: str = "codebook"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, numcodes: int = 256, codebooksize: int = 256, maxsteps: int = 500) -> None:
        if numcodes <= 0 or maxsteps <= 0:
            raise ValueError("numcodes and maxsteps must be > 0")
        self.numcodes = numcodes
        self.codebooksize = codebooksize
        self.maxsteps = maxsteps

    def setup(self) -> None:
        return None

    def run(self, dataloader: Any | None = None) -> dict[str, Any]:
        """Train the quantizer trio.

        Args:
            dataloader: optional ``[batch, dim]`` tensor iterator.

        Raises:
            requiresenvironment: torch missing.
        """
        if dataloader is None:
            raise requiresresource("phase:codebook requires a dataloader")
        trainer = registry.create(
            "quantizer",
            "trainer",
            numcodes=self.numcodes,
            dim=64,
            numstages=4,
            maxsteps=self.maxsteps,
        )
        result = trainer.run(dataloader)
        getlogger("braid.phase.codebook").info("codebook.train.complete", steps=result.get("steps", 0))
        return result

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
