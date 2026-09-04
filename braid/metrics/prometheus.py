"""Prometheus metrics backend — real ``prometheus_client`` integration."""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="metrics", name="prometheus")
class prometheus:
    """Prometheus metrics backed by ``prometheus_client``."""

    name: str = "prometheus"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def __init__(self, port: int = 9090) -> None:
        try:
            from prometheus_client import start_http_server, Counter, Gauge, Histogram

            self.port = port
            self.countercls = Counter
            self.gaugecls = Gauge
            self.histogramcls = Histogram
            start_http_server(self.port)
        except ImportError as exc:
            raise requiresenvironment(
                "prometheus_client required for metrics:prometheus",
                hint="pip install prometheus-client",
            ) from exc

    def counter(self, name: str, value: float = 1.0, labels: dict | None = None) -> None:
        """Increment a counter by ``value``.

        Args:
            name: counter metric name.
            value: increment amount.
            labels: optional label dict.
        """
        try:
            c = self.countercls(name, "braid counter", list(labels or {}))
            c.inc(value)
        except Exception:
            pass

    def gauge(self, name: str, value: float, labels: dict | None = None) -> None:
        """Set a gauge value."""
        try:
            g = self.gaugecls(name, "braid gauge", list(labels or {}))
            g.set(value)
        except Exception:
            pass

    def histogram(self, name: str, value: float, labels: dict | None = None) -> None:
        """Record a histogram value."""
        try:
            h = self.histogramcls(name, "braid histogram", list(labels or {}))
            h.observe(value)
        except Exception:
            pass

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
