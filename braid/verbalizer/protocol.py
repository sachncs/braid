"""Verbalizer category Protocol."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class verbalizer(Protocol):
    """A strategy for turning context into a textual prompt."""

    def render(self, context: dict[str, Any]) -> str: ...
