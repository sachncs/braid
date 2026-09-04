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

    Raises:
        requiresenvironment: if ``transformers`` is not installed.
    """

    name: str = "hf"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "idempotent", "observable"})

    def __init__(self, name: str, token: str | None = None) -> None:
        """Initialize.

        Args:
            name: HF tokenizer name (e.g., ``openbmb/MiniCPM5-1B``).
            token: optional HF token for gated models.

        Raises:
            requiresenvironment: if ``transformers`` is unavailable.
        """
        try:
            from transformers import AutoTokenizer
            self._tok: Any = AutoTokenizer.from_pretrained(name, token=token)
        except ImportError as exc:
            raise requiresenvironment(
                "transformers is required for tokenizer:hf",
                hint="pip install transformers",
            ) from exc

    def encode(self, text: str) -> list[int]:
        """Encode ``text`` to a list of token ids."""
        return list(self._tok.encode(text))

    def decode(self, ids: Iterable[int]) -> str:
        """Decode ``ids`` back to text."""
        return self._tok.decode(list(ids))

    def count(self, text: str) -> int:
        """Return the token count for ``text``."""
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
