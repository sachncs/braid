"""tiktoken tokenizer wrapper."""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.registry import registry


@registry.register(category="tokenizer", name="tiktoken")
class tiktoken:
    """tiktoken (OpenAI's BPE) wrapper.

    Attributes:
        encoding: encoding name (``"cl100k_base"`` etc.).
    """

    name: str = "tiktoken"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, encoding: str = "cl100k_base") -> None:
        self.encoding = encoding
        self._enc: Any | None = None
        try:
            import tiktoken

            self._enc = tiktoken.get_encoding(encoding)
        except Exception:  # noqa: BLE001 — degraded mode
            self._enc = None

    def encode(self, text: str) -> list[int]:
        if self._enc is None:
            return [ord(c) for c in text]
        return list(self._enc.encode(text))

    def decode(self, ids: Iterable[int]) -> str:
        if self._enc is None:
            return "".join(chr(int(i)) for i in ids)
        return self._enc.decode(list(ids))

    def count(self, text: str) -> int:
        return len(self.encode(text))

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"tokenizer:tiktoken:{self.encoding}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
