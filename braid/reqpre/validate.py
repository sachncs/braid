"""Schema validation preprocessing."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.core.error import validationerror


@registry.register(category="reqpre", name="validate")
class validate:
    """Schema validation against a list of required keys."""

    name: str = "validate"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def __init__(self, required: list[str] | None = None) -> None:
        self.required = set(required or ["userid", "context", "candidates"])

    def process(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate the request."""
        missing = self.required - set(request.keys())
        if missing:
            raise validationerror(f"missing required keys: {sorted(missing)}")
        return request

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
