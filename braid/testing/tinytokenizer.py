"""Tiny tokenizer wrapper for tests."""

from __future__ import annotations

from typing import Iterable


class tinytokenizer:
    """A trivial whitespace tokenizer.

    Real tests use ``braid.tokenizer.hf``; this exists for protocol
    conformance tests that need a no-network hermetic tokenizer.
    """

    def encode(self, text: str) -> list[int]:
        """Encode ``text`` as a list of codepoints.

        Args:
            text: input string.

        Returns:
            A list of integer codepoints.
        """
        return [ord(c) for c in text]

    def decode(self, ids: Iterable[int]) -> str:
        """Decode ``ids`` back to text.

        Args:
            ids: integer ids.

        Returns:
            The decoded string.
        """
        return "".join(chr(i) for i in ids)

    def count(self, text: str) -> int:
        """Return the token count for ``text``.

        Args:
            text: input string.

        Returns:
            Number of tokens.
        """
        return len(self.encode(text))
