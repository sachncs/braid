"""Environment-variable secret provider. Fail-fast on missing keys."""

from __future__ import annotations

import os
from typing import Any

from braid.core.error import ioerror
from braid.core.registry import registry


@registry.register(category="secret", name="env")
class env:
    """Reads secrets from environment variables.

    Use ``env.get(name)`` in your code; raises if ``name`` is unset.
    """

    name: str = "env"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def get(self, name: str) -> str:
        """Return the secret value or raise ``ioerror``.

        Args:
            name: environment variable name.

        Returns:
            The variable's string value.

        Raises:
            ioerror: if the variable is missing.
        """
        v = os.environ.get(name)
        if v is None:
            raise ioerror(f"env var missing: {name}", retryable=False)
        return v

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
