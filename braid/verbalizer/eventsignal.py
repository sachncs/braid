"""Event-signal verbalizer.

The default GenRec-style verbalizer: emit high-signal events with rich
metadata, drop noise, summarize old history.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.truncation.signalweighted import signalweighted
from braid.template.fstring import fstring


@registry.register(category="verbalizer", name="eventsignal")
class eventsignal:
    """Verbalize using signal-weighted truncation and an f-string template."""

    name: str = "eventsignal"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    DEFAULT_TEMPLATE = (
        "user profile: {user}\n"
        "context: {context}\n"
        "history (signal-weighted, most recent first):\n"
        "{history}\n"
        "candidates:\n{candidates}\n"
        "task: rank the candidates by expected long-term satisfaction."
    )

    def __init__(self, budget: int = 20, template: str | None = None) -> None:
        self.truncator = signalweighted(budget=budget)
        self.template = fstring(template or self.DEFAULT_TEMPLATE)

    def render(self, context: dict[str, Any]) -> str:
        events = context.get("history", [])
        kept = self.truncator.fit(events)
        history = "\n".join(
            f"- {e.get('kind', 'play')} item={e.get('itemid')} dur={e.get('duration', 0)}"
            for e in kept
        )
        return self.template.render(
            user=context.get("user", "anon"),
            context=context.get("metadata", {}),
            history=history or "(none)",
            candidates="\n".join(f"item {i}" for i in context.get("candidates", [])),
        )

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"verbalizer:eventsignal:{self.truncator.budget}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
