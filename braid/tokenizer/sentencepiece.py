"""SentencePiece tokenizer wrapper."""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.registry import registry


@registry.register(category="tokenizer", name="sentencepiece")
class sentencepiece:
    """SentencePiece tokenizer wrapper.

    Attributes:
        modelpath: path to a ``.model`` file.
    """

    name: str = "sentencepiece"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, modelpath: str) -> None:
        self.modelpath = modelpath
        self._sp: Any | None = None
        try:
            import sentencepiece as spm

            self._sp = spm.SentencePieceProcessor()
            self._sp.Load(modelpath)
        except Exception:  # noqa: BLE001 — degraded mode
            self._sp = None

    def encode(self, text: str) -> list[int]:
        if self._sp is None:
            return [ord(c) for c in text]
        return list(self._sp.EncodeAsIds(text))

    def decode(self, ids: Iterable[int]) -> str:
        if self._sp is None:
            return "".join(chr(int(i)) for i in ids)
        return self._sp.DecodeIds(list(ids))

    def count(self, text: str) -> int:
        return len(self.encode(text))

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"tokenizer:spm:{self.modelpath}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
