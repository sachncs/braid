"""Hugging Face tokenizer wrapper."""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.registry import registry


@registry.register(category="tokenizer", name="hf")
class hf:
    """Wraps a Hugging Face ``AutoTokenizer``.

    Attributes:
        name: model name or path.
        token: optional HF token.
    """

    name: str = "hf"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "idempotent", "observable"})

    def __init__(self, name: str, token: str | None = None) -> None:
        """Initialize.

        Args:
            name: HF tokenizer name (e.g., ``openbmb/MiniCPM5-1B``).
            token: optional HF token for gated models.
        """
        self.name = name
        self.token = token
        self._tok: Any | None = None
        try:
            from transformers import AutoTokenizer

            self._tok = AutoTokenizer.from_pretrained(name, token=token)
        except Exception:  # noqa: BLE001 — degraded mode
            self._tok = None

    def encode(self, text: str) -> list[int]:
        if self._tok is None:
            return [ord(c) for c in text]
        return list(self._tok.encode(text))

    def decode(self, ids: Iterable[int]) -> str:
        if self._tok is None:
            return "".join(chr(int(i)) for i in ids)
        return self._tok.decode(list(ids))

    def count(self, text: str) -> int:
        return len(self.encode(text))

    def cacheget(self, key: str) -> Any | None:
        return self._tok if key == self.name else None

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
