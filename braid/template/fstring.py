"""F-string template engine."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="template", name="fstring")
class fstring:
    """Renders prompts via Python ``str.format_map``.

    Uses ``str.format_map`` for safety — no eval.
    """

    name: str = "fstring"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, template: str) -> None:
        self.template = template

    def render(self, **kwargs: Any) -> str:
        """Render the template."""
        return self.template.format_map(kwargs)

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"template:fstring:{self.template}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
