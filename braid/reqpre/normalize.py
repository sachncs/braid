"""Normalize request preprocessing."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="reqpre", name="normalize")
class normalize:
    """Lowercase, trim, and collapse whitespace in fields."""

    name: str = "normalize"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def process(self, request: dict[str, Any]) -> dict[str, Any]:
        """Normalize a request dict."""
        out: dict[str, Any] = {}
        for k, v in request.items():
            if isinstance(v, str):
                out[k] = " ".join(v.strip().lower().split())
            elif isinstance(v, dict):
                out[k] = self.process(v)
            elif isinstance(v, list):
                out[k] = [self.process(x) if isinstance(x, dict) else x for x in v]
            else:
                out[k] = v
        return out

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
