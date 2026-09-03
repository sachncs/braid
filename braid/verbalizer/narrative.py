"""Narrative verbalizer."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.template.fstring import fstring


@registry.register(category="verbalizer", name="narrative")
class narrative:
    """Render the user history as a flowing narrative paragraph."""

    name: str = "narrative"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self) -> None:
        self.template = fstring(
            "Recently, user {user} {narrative}. Based on this, recommend from {candidates}."
        )

    def render(self, context: dict[str, Any]) -> str:
        events = context.get("history", [])[-30:]
        parts: list[str] = []
        for e in events:
            k = e.get("kind", "play")
            i = e.get("itemid")
            d = e.get("duration", 0)
            if k == "thumbup":
                parts.append(f"thumb-up'd item {i}")
            elif k == "play" and d > 60:
                parts.append(f"watched item {i} for {int(d)}s")
            else:
                parts.append(f"interacted with item {i}")
        narrative = ", ".join(parts) if parts else "had no recent activity"
        return self.template.render(
            user=context.get("user", "anon"),
            narrative=narrative,
            candidates=", ".join(str(i) for i in context.get("candidates", [])),
        )

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return "verbalizer:narrative:v1"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
