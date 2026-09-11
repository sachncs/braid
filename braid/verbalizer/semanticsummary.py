"""Semantic-summary verbalizer.

Uses an LLM-style human-readable summary of the user's preferences
rather than a raw event list.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.truncation.diversity import diversity as divtrunc
from braid.template.fstring import fstring


@registry.register(category="verbalizer", name="semanticsummary")
class semanticsummary:
    """Verbalize using a deterministic semantic summary of history."""

    name: str = "semanticsummary"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self) -> None:
        self.truncator = divtrunc(budget=15)
        self.template = fstring("taste summary for {user}: {tastes}; rank from {candidates}.")

    def render(self, context: dict[str, Any]) -> str:
        kept = self.truncator.fit(context.get("history", []))
        genres: dict[str, int] = {}
        for e in kept:
            g = e.get("genre") or "unknown"
            genres[g] = genres.get(g, 0) + 1
        tastes = ", ".join(f"{k} ({v})" for k, v in sorted(genres.items(), key=lambda kv: -kv[1]))
        return self.template.render(
            user=context.get("user", "anon"),
            tastes=tastes or "(no history)",
            candidates=",".join(str(i) for i in context.get("candidates", [])),
        )

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return "verbalizer:semanticsummary:v1"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
