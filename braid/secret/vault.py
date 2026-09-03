"""HashiCorp Vault secret provider."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.core.error import ioerror


@registry.register(category="secret", name="vault")
class vault:
    """HashiCorp Vault secret provider."""

    name: str = "vault"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "cachable", "observable"})

    def __init__(self, url: str, token: str, mountpoint: str = "secret") -> None:
        self.url = url
        self.token = token
        self.mountpoint = mountpoint
        self._client: Any | None = None
        self._connect()

    def _connect(self) -> None:
        try:
            import hvac

            self._client = hvac.Client(url=self.url, token=self.token)
        except Exception:  # noqa: BLE001
            self._client = None

    def get(self, path: str, key: str | None = None) -> str:
        """Fetch ``path`` (and ``key``, if KV2)."""
        if self._client is None:
            self._connect()
        if self._client is None:
            raise ioerror("vault client unavailable", retryable=True)
        try:
            resp = self._client.secrets.kv.v2.read_secret(path, mount_point=self.mountpoint)
            data = resp["data"]["data"]
            if key:
                return data[key]
            return str(data)
        except Exception as exc:  # noqa: BLE001
            raise ioerror(f"vault read failed: {exc}", retryable=True) from exc

    async def aget(self, path: str, key: str | None = None) -> str:
        return self.get(path, key)

    def cacheget(self, key: str) -> str | None:
        return None

    def cacheput(self, key: str, value: str) -> None:
        return None

    def cacheinvalidate(self, key: str) -> None:
        return None

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
