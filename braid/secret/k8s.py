"""Kubernetes secret provider."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.core.error import ioerror


@registry.register(category="secret", name="k8s")
class k8s:
    """Kubernetes-secret provider via the K8s API."""

    name: str = "k8s"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "cachable", "observable"})

    def __init__(self, namespace: str = "default") -> None:
        self.namespace = namespace
        self._client: Any | None = None
        self._connect()

    def _connect(self) -> None:
        try:
            from kubernetes import client, config

            config.load_incluster_config()
            self._client = client.CoreV1Api()
        except Exception:  # noqa: BLE001
            self._client = None

    def get(self, name: str, key: str | None = None) -> str:
        """Read a Kubernetes secret."""
        if self._client is None:
            self._connect()
        if self._client is None:
            raise ioerror("k8s client unavailable", retryable=False)
        try:
            sec = self._client.read_namespaced_secret(name, self.namespace)
            if key:
                from base64 import b64decode

                return b64decode(sec.data[key]).decode("utf-8")
            return str(sec.data)
        except Exception as exc:  # noqa: BLE001
            raise ioerror(f"k8s read failed: {exc}", retryable=False) from exc

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
