"""tiktoken token counter."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.tokenizer.tiktoken import tiktoken as tt


@registry.register(category="tokencounter", name="tiktokencount")
class tiktokencount:
    """Counts tokens using tiktoken."""

    name: str = "tiktokencount"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, encoding: str = "cl100k_base") -> None:
        self.tokenizer = tt(encoding)

    def count(self, text: str) -> int:
        return self.tokenizer.count(text)

    def countmany(self, texts: list[str]) -> list[int]:
        return [self.count(t) for t in texts]

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"tokencounter:tiktokencount:{self.tokenizer.encoding}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
