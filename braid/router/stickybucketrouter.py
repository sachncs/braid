"""Sticky-bucket A/B router."""

from __future__ import annotations

import hashlib
from typing import Any

from braid.core.registry import registry


@registry.register(category="router", name="stickybucketrouter")
class stickybucketrouter:
    """Hash-based sticky bucketing router."""

    name: str = "stickybucketrouter"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency", "async", "idempotent"})

    def __init__(self, arms: list[str] | None = None, nbuckets: int = 100) -> None:
        self.arms = arms or ["control", "treatment"]
        self.nbuckets = nbuckets

    def route(self, key: str | None = None) -> str:
        """Hash the key, mod buckets, pick an arm."""
        if not key:
            return self.arms[0]
        h = int(hashlib.sha1(str(key).encode("utf-8")).hexdigest(), 16)
        return self.arms[h % self.nbuckets % len(self.arms)]

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"router:sticky:{self.arms}:{self.nbuckets}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
