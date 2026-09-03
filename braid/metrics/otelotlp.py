"""OpenTelemetry OTLP metrics backend."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="metrics", name="otelotlp")
class otelotlp:
    """OTLP metrics backend."""

    name: str = "otelotlp"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency", "async"})

    def __init__(self, endpoint: str = "http://localhost:4317") -> None:
        self.endpoint = endpoint
        self._meter: Any | None = None
        self._start()

    def _start(self) -> None:
        try:
            from opentelemetry import metrics
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.exporter.otlp.metrics_exporter import OTLPMetricsExporter

            provider = MeterProvider()
            provider.start()
            self._meter = metrics.get_meter("braid")
        except Exception:  # noqa: BLE001
            self._meter = None

    def counter(self, name: str, value: float = 1.0, labels: dict | None = None) -> None:
        if self._meter is None:
            return
        try:
            c = self._meter.create_counter(name)
            c.add(value, attributes=labels or {})
        except Exception:  # noqa: BLE001
            return

    def gauge(self, name: str, value: float, labels: dict | None = None) -> None:
        if self._meter is None:
            return
        try:
            g = self._meter.create_up_down_counter(name)
            g.add(value - g._lastvalue if hasattr(g, "_lastvalue") else value, attributes=labels or {})
        except Exception:  # noqa: BLE001
            return

    def histogram(self, name: str, value: float, labels: dict | None = None) -> None:
        if self._meter is None:
            return
        try:
            h = self._meter.create_histogram(name)
            h.record(value, attributes=labels or {})
        except Exception:  # noqa: BLE001
            return

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
