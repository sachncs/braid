"""Jinja2 template engine."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="template", name="jinja2")
class jinja2:
    """Renders prompts via Jinja2."""

    name: str = "jinja2"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "idempotent", "observable"})

    def __init__(self, template: str) -> None:
        try:
            import jinja2 as _j
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("jinja2 required for template:jinja2") from exc
        self.env = _j.Environment(autoescape=False)
        self.tpl = self.env.from_string(template)
        self.template_source = template

    def render(self, **kwargs: Any) -> str:
        """Render the template with keyword arguments."""
        return self.tpl.render(**kwargs)

    def cacheget(self, key: str) -> str | None:
        return self.template_source if key == self.template_source else None

    def cacheput(self, key: str, value: str) -> None:
        return None

    def cacheinvalidate(self, key: str) -> None:
        return None

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"template:jinja2:{self.template_source}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
