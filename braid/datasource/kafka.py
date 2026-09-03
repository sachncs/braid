"""Kafka streaming datasource."""

from __future__ import annotations

from typing import Any, Iterator

from braid.core.registry import registry


@registry.register(category="datasource", name="kafka")
class kafka:
    """Tail a Kafka topic and yield events as dicts.

    Attributes:
        brokers: comma-separated bootstrap servers.
        topic: topic name.
        groupid: consumer group id.
    """

    name: str = "kafka"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"streamable", "async", "observable", "circuitbreaker"})

    def __init__(self, brokers: str, topic: str, groupid: str = "braid") -> None:
        """Initialize the Kafka consumer source.

        Args:
            brokers: comma-separated bootstrap servers.
            topic: topic to consume.
            groupid: consumer group id.
        """
        self.brokers = brokers
        self.topic = topic
        self.groupid = groupid
        self._stop = False

    def read(self) -> Iterator[dict[str, Any]]:
        """Yield messages from Kafka as parsed dicts.

        Returns an empty iterator if ``kafka-python`` is not installed
        (graceful degradation for environments without the driver).

        Yields:
            Decoded JSON messages.
        """
        try:
            from kafka import KafkaConsumer
            import json
        except ImportError:
            return
        consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.brokers.split(","),
            group_id=self.groupid,
            enable_auto_commit=True,
            auto_offset_reset="latest",
        )
        for msg in consumer:
            if self._stop:
                break
            try:
                yield json.loads(msg.value)
            except Exception:  # noqa: BLE001 — skip malformed
                continue

    async def aread(self) -> Any:
        try:
            from aiokafka import AIOKafkaConsumer
            import json
        except ImportError:
            return []
        consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.brokers.split(","),
            group_id=self.groupid,
        )
        await consumer.start()
        try:
            out = []
            async for msg in consumer:
                try:
                    out.append(json.loads(msg.value))
                except Exception:  # noqa: BLE001
                    continue
            return out
        finally:
            await consumer.stop()

    def stop(self) -> None:
        """Stop an in-progress read loop."""
        self._stop = True

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.datasource.kafka.lag", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
