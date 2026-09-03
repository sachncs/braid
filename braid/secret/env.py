"""Environment-variable secret provider."""

from __future__ import annotations

import os
from typing import Any

from braid.core.registry import registry
from braid.core.error import ioerror


@registry.register(category="secret", name="env")
class env:
    """Reads secrets from environment variables."""

    name: str = "env"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def get(self, name: str) -> str:
        """Return the secret value or raise ``ioerror``."""
        v = os.environ.get(name)
        if v is None:
            raise ioerror(f"env var missing: {name}", retryable=False)
        return v

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
