"""Hugging Face tokenizer wrapper."""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="tokenizer", name="hf")
class hf:
    """Wraps a Hugging Face ``AutoTokenizer``.

    Attributes:
        name: model name or path.
        token: optional HF token for gated models.
        tok: the loaded tokenizer (public).
    """

    name: str = "hf"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "idempotent", "observable"})

    def __init__(self, name: str, token: str | None = None) -> None:
        try:
            from transformers import AutoTokenizer

            self.name = name
            self.token = token
            self.tok: Any = AutoTokenizer.from_pretrained(name, token=token)
        except ImportError as exc:
            raise requiresenvironment(
                "transformers required for tokenizer:hf",
                hint="pip install transformers",
            ) from exc

    def encode(self, text: str) -> list[int]:
        return list(self.tok.encode(text))

    def decode(self, ids: Iterable[int]) -> str:
        return self.tok.decode(list(ids))

    def count(self, text: str) -> int:
        return len(self.encode(text))

    def cacheget(self, key: str) -> Any | None:
        return self.tok if key == self.name else None

    def cacheput(self, key: str, value: Any) -> None:
        return None

    def cacheinvalidate(self, key: str) -> None:
        return None

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"tokenizer:hf:{self.name}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
