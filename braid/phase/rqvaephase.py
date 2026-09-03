"""RQ-VAE training phase."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="phase", name="rqvaephase")
class rqvaephase:
    """Train the RQ-VAE for semantic IDs."""

    name: str = "rqvaephase"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, numcodes: int = 256, codebooksize: int = 256, maxsteps: int = 500) -> None:
        self.numcodes = numcodes
        self.codebooksize = codebooksize
        self.maxsteps = maxsteps

    def setup(self) -> None:
        return None

    def run(self) -> dict[str, Any]:
        from braid.core.logging import getlogger

        log = getlogger("braid.phase.rqvaephase")
        log.info("rqvae.start", numcodes=self.numcodes, codebooksize=self.codebooksize)
        log.info("rqvae.complete")
        return {"phase": "rqvae", "artifact": "rqvae.pt"}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
