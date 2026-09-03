"""OpenTelemetry OTLP tracing backend."""

from __future__ import annotations

import contextlib
from typing import Any

from braid.core.registry import registry


@registry.register(category="tracing", name="otlp")
class otlp:
    """OTLP tracing backend."""

    name: str = "otlp"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "async"})

    def __init__(self, endpoint: str = "http://localhost:4317") -> None:
        self.endpoint = endpoint
        self._tracer: Any | None = None
        self._start()

    def _start(self) -> None:
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter

            provider = TracerProvider()
            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=self.endpoint)))
            trace.set_tracer_provider(provider)
            self._tracer = trace.get_tracer("braid")
        except Exception:  # noqa: BLE001
            self._tracer = None

    @contextlib.contextmanager
    def span(self, name: str, **attrs: Any):
        """Open a span if tracing is enabled."""
        if self._tracer is None:
            yield None
            return
        with self._tracer.start_as_current_span(name) as sp:
            for k, v in attrs.items():
                sp.set_attribute(k, v)
            yield sp

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
