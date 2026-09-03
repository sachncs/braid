"""No-op authentication (open access)."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="auth", name="noauth")
class noauth:
    """No-op authentication."""

    name: str = "noauth"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"lowlatency"})

    def authenticate(self, key: str | None = None) -> dict[str, Any]:
        return {"principal": "anon", "kind": "noauth"}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
