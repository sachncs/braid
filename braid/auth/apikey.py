"""Static API-key authentication."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.core.error import validationerror


@registry.register(category="auth", name="apikey")
class apikey:
    """Compare against a set of allowed API keys."""

    name: str = "apikey"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def __init__(self, allowed: list[str] | None = None) -> None:
        self.allowed = set(allowed or [])

    def authenticate(self, key: str) -> dict[str, Any]:
        """Return the principal dict or raise ``validationerror``."""
        if key not in self.allowed:
            raise validationerror("invalid api key", retryable=False)
        return {"principal": key, "kind": "apikey"}

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.auth.apikey.failures", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
