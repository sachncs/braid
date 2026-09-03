"""Gradient accumulation helpers."""

from __future__ import annotations

from typing import Any


class gradaccum:
    """Accumulates gradients over ``steps`` micro-batches."""

    def __init__(self, steps: int = 1) -> None:
        self.steps = max(1, steps)
        self._i = 0

    def boundary(self) -> bool:
        """True iff we should take an optimizer step now."""
        self._i += 1
        boundary = (self._i % self.steps) == 0
        return boundary

    def reset(self) -> None:
        self._i = 0
