"""Mustache template engine."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="template", name="mustache")
class mustache:
    """Renders prompts via pystache (Mustache spec)."""

    name: str = "mustache"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"idempotent", "observable"})

    def __init__(self, template: str) -> None:
        try:
            import pystache
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("pystache required for template:mustache") from exc
        self.template = template
        self.renderer = pystache.Renderer()

    def render(self, **kwargs: Any) -> str:
        """Render the template via Mustache."""
        return self.renderer.render(self.template, kwargs)

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"template:mustache:{self.template}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
