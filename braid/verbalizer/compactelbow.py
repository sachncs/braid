"""Compact-elbow verbalizer.

Uses the elbow truncation strategy combined with a templated prompt.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.truncation.elbow import elbow as elbowtrunc
from braid.template.fstring import fstring


@registry.register(category="verbalizer", name="compactelbow")
class compactelbow:
    """Compact verbalizer using the elbow truncation point."""

    name: str = "compactelbow"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, elbowevents: int = 30) -> None:
        self.truncator = elbowtrunc(elbowevents=elbowevents)
        self.template = fstring("user {user}; recent: {history}; candidates: {cands}; rank them.")

    def render(self, context: dict[str, Any]) -> str:
        kept = self.truncator.fit(context.get("history", []))
        history = "; ".join(f"{e.get('kind')}#{e.get('itemid')}" for e in kept)
        return self.template.render(
            user=context.get("user", "anon"),
            history=history or "(none)",
            cands=",".join(str(i) for i in context.get("candidates", [])),
        )

    def setelbow(self, n: int) -> None:
        """Update the elbow point at runtime."""
        self.truncator.setelbow(n)

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"verbalizer:compactelbow:{self.truncator.elbowevents}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
