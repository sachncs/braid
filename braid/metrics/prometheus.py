"""Prometheus metrics backend."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="metrics", name="prometheus")
class prometheus:
    """Prometheus metrics backend."""

    name: str = "prometheus"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def __init__(self, port: int = 9090) -> None:
        self.port = port
        self.client: Any | None = None
        self.start()

    def start(self) -> None:
        try:
            from prometheus_client import start_http_server, Counter, Gauge, Histogram

            self.countercls = Counter
            self.gaugecls = Gauge
            self.histogramcls = Histogram
            self.server = start_http_server(self.port)
        except Exception:  # noqa: BLE001
            self.countercls = None

    def counter(self, name: str, value: float = 1.0, labels: dict | None = None) -> None:
        if self.countercls is None:
            return
        try:
            c = self.countercls(name, "braid counter", list(labels or {}))
            c.inc(value)
        except Exception:  # noqa: BLE001
            return

    def gauge(self, name: str, value: float, labels: dict | None = None) -> None:
        if self.gaugecls is None:
            return
        try:
            g = self.gaugecls(name, "braid gauge", list(labels or {}))
            g.set(value)
        except Exception:  # noqa: BLE001
            return

    def histogram(self, name: str, value: float, labels: dict | None = None) -> None:
        if self.histogramcls is None:
            return
        try:
            h = self.histogramcls(name, "braid histogram", list(labels or {}))
            h.observe(value)
        except Exception:  # noqa: BLE001
            return

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
