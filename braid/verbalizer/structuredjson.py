"""Structured JSON verbalizer."""

from __future__ import annotations

import json
from typing import Any

from braid.core.registry import registry


@registry.register(category="verbalizer", name="structuredjson")
class structuredjson:
    """Emit a JSON-structured prompt."""

    name: str = "structuredjson"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def render(self, context: dict[str, Any]) -> str:
        return json.dumps({"task": "rank", **context}, default=str)

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return "verbalizer:structuredjson:v1"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
