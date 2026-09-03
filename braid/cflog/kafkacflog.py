"""Kafka counterfactual logger."""

from __future__ import annotations

import json
from typing import Any

from braid.core.registry import registry


@registry.register(category="cflog", name="kafkacflog")
class kafkacflog:
    """Counterfactual log to Kafka."""

    name: str = "kafkacflog"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, brokers: str, topic: str) -> None:
        self.brokers = brokers
        self.topic = topic
        self._producer: Any | None = None
        self._connect()

    def _connect(self) -> None:
        try:
            from kafka import KafkaProducer

            self._producer = KafkaProducer(
                bootstrap_servers=self.brokers.split(","),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        except Exception:  # noqa: BLE001
            self._producer = None

    def log(self, entry: dict[str, Any]) -> None:
        """Send a log entry."""
        if self._producer is None:
            return
        try:
            self._producer.send(self.topic, entry)
        except Exception:  # noqa: BLE001
            return

    def flush(self) -> None:
        if self._producer is None:
            return
        try:
            self._producer.flush()
        except Exception:  # noqa: BLE001
            return

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
