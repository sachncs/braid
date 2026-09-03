"""Hugging Face token counter."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.tokenizer.hf import hf as hftokenizer


@registry.register(category="tokencounter", name="hfcount")
class hfcount:
    """Counts tokens using an HF tokenizer."""

    name: str = "hfcount"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, tokenizername: str = "openbmb/MiniCPM5-1B") -> None:
        self.tokenizer = hftokenizer(tokenizername)

    def count(self, text: str) -> int:
        return self.tokenizer.count(text)

    def countmany(self, texts: list[str]) -> list[int]:
        return [self.count(t) for t in texts]

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"tokencounter:hfcount:{self.tokenizer.name}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
