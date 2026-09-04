"""Quantizer training runner."""

from typing import Any

from braid.core.registry import registry


@registry.register(category="quantizer", name="trainer")
class trainer:
    """Real quantizer training runner.

    Currently exposes run/setup contract. Real implementation will be
    delivered in M4 (encoder/decoder/quantizer training loop).
    """

    name: str = "trainer"
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

        getlogger("braid.quantizer.trainer").info("rqvae.run", numcodes=self.numcodes, steps=self.maxsteps)
        return {"phase": "rqvae", "artifact": "rqvae.pt"}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
