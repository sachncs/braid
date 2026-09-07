"""tiktoken tokenizer wrapper."""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="tokenizer", name="tiktoken")
class tiktoken:
    """tiktoken (OpenAI's BPE) wrapper.

    Attributes:
        encoding: encoding name (``"cl100k_base"`` etc.).
        enc: the underlying tiktoken encoding.
    """

    name: str = "tiktoken"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, encoding: str = "cl100k_base") -> None:
        try:
            import tiktoken

            self.enc = tiktoken.get_encoding(encoding)
        except ImportError as exc:
            raise requiresenvironment(
                "tiktoken is required for tokenizer:tiktoken",
                hint="pip install tiktoken",
            ) from exc
        self.encoding = encoding

    def encode(self, text: str) -> list[int]:
        return list(self.enc.encode(text))

    def decode(self, ids: Iterable[int]) -> str:
        return self.enc.decode(list(ids))

    def count(self, text: str) -> int:
        return len(self.encode(text))

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"tokenizer:tiktoken:{self.encoding}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
