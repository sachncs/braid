"""Jaeger tracing backend (via OTLP)."""

from __future__ import annotations

from typing import Any

from braid.tracing.otlp import otlp as otlptracing


@registry.register(category="tracing", name="jaeger")
class jaeger:
    """Jaeger tracing adapter — reuses the OTLP exporter with Jaeger endpoint."""

    name: str = "jaeger"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "async"})

    def __init__(self, endpoint: str = "http://localhost:14268/api/traces") -> None:
        self._inner = otlptracing(endpoint=endpoint)

    def span(self, name: str, **attrs: Any):
        return self._inner.span(name, **attrs)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
