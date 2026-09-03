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
        self._client: Any | None = None
        self._start()

    def _start(self) -> None:
        try:
            from prometheus_client import start_http_server, Counter, Gauge, Histogram

            self._countercls = Counter
            self._gaugecls = Gauge
            self._histogramcls = Histogram
            self._server = start_http_server(self.port)
        except Exception:  # noqa: BLE001
            self._countercls = None

    def counter(self, name: str, value: float = 1.0, labels: dict | None = None) -> None:
        if self._countercls is None:
            return
        try:
            c = self._countercls(name, "braid counter", list(labels or {}))
            c.inc(value)
        except Exception:  # noqa: BLE001
            return

    def gauge(self, name: str, value: float, labels: dict | None = None) -> None:
        if self._gaugecls is None:
            return
        try:
            g = self._gaugecls(name, "braid gauge", list(labels or {}))
            g.set(value)
        except Exception:  # noqa: BLE001
            return

    def histogram(self, name: str, value: float, labels: dict | None = None) -> None:
        if self._histogramcls is None:
            return
        try:
            h = self._histogramcls(name, "braid histogram", list(labels or {}))
            h.observe(value)
        except Exception:  # noqa: BLE001
            return

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
