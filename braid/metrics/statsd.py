"""StatsD metrics backend."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="metrics", name="statsd")
class statsd:
    """StatsD UDP metrics backend."""

    name: str = "statsd"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def __init__(self, host: str = "localhost", port: int = 8125) -> None:
        self.host = host
        self.port = port
        self._client: Any | None = None
        try:
            import statsd

            self._client = statsd.StatsClient(host=host, port=port)
        except Exception:  # noqa: BLE001
            self._client = None

    def counter(self, name: str, value: float = 1.0, labels: dict | None = None) -> None:
        if self._client is None:
            return
        try:
            self._client.incr(name, value)
        except Exception:  # noqa: BLE001
            return

    def gauge(self, name: str, value: float, labels: dict | None = None) -> None:
        if self._client is None:
            return
        try:
            self._client.gauge(name, value)
        except Exception:  # noqa: BLE001
            return

    def histogram(self, name: str, value: float, labels: dict | None = None) -> None:
        if self._client is None:
            return
        try:
            self._client.timing(name, value)
        except Exception:  # noqa: BLE001
            return

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
