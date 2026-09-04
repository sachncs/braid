"""Codebook (RQ-VAE) training phase.

Real implementation arrives in O4 (encodes → quantize → decode pipeline).
"""

from __future__ import annotations

from typing import Any

from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="phase", name="codebook")
class codebook:
    """Codebook training phase.

    Trains the encoder/decoder/quantizer trio used for semantic-ID scoring.

    Attributes:
        numcodes: codes per residual stage.
        codebooksize: codes per stage (alias of ``numcodes``).
        maxsteps: training steps.
    """

    name: str = "codebook"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, numcodes: int = 256, codebooksize: int = 256, maxsteps: int = 500) -> None:
        """Initialize.

        Args:
            numcodes: codes per stage. Defaults to 256.
            codebooksize: codes per stage. Defaults to 256.
            maxsteps: training steps. Defaults to 500.
        """
        self.numcodes = numcodes
        self.codebooksize = codebooksize
        self.maxsteps = maxsteps

    def setup(self) -> None:
        return None

    def run(self) -> dict[str, Any]:
        log = getlogger("braid.phase.codebook")
        log.info("codebook.start", numcodes=self.numcodes, steps=self.maxsteps)
        return {"phase": "codebook", "artifact": "codebook.pt"}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
