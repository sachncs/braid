"""Approximate (per-character) token counter."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="tokencounter", name="approxcount")
class approxcount:
    """Approximate token count from whitespace-separated words + punctuation.

    Useful when a real tokenizer is unavailable.

    Attributes:
        charsperratio: heuristic characters per token.
    """

    name: str = "approxcount"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, charsperratio: float = 4.0) -> None:
        if charsperratio <= 0:
            raise ValueError("charsperratio must be > 0")
        self.charsperratio = charsperratio

    def count(self, text: str) -> int:
        """Approximate token count from characters / ratio."""
        if not text:
            return 0
        return max(1, int(len(text) / self.charsperratio))

    def countmany(self, texts: list[str]) -> list[int]:
        return [self.count(t) for t in texts]

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"tokencounter:approxcount:{self.charsperratio}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
