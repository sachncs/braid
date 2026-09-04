"""SentencePiece tokenizer wrapper."""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.error import requiresenvironment
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
        try:
            import sentencepiece as spm

            self._sp = spm.SentencePieceProcessor()
            self._sp.Load(modelpath)
        except ImportError as exc:
            raise requiresenvironment(
                "sentencepiece is required for tokenizer:sentencepiece",
                hint="pip install sentencepiece",
            ) from exc

    def encode(self, text: str) -> list[int]:
        return list(self._sp.EncodeAsIds(text))

    def decode(self, ids: Iterable[int]) -> str:
        return self._sp.DecodeIds(list(ids))

    def count(self, text: str) -> int:
        return len(self.encode(text))

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"tokenizer:spm:{self.modelpath}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
