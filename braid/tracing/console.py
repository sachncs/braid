"""Console tracing (debug only)."""

from __future__ import annotations

import contextlib
from typing import Any

from braid.core.registry import registry


@registry.register(category="tracing", name="console")
class console:
    """Console tracing backend (prints to stderr)."""

    name: str = "console"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})  # not async-capable

    @contextlib.contextmanager
    def span(self, name: str, **attrs: Any):
        """Print span start/end to stderr."""
        import sys

        print(f"[trace] span.start {name} {attrs}", file=sys.stderr)
        try:
            yield None
        finally:
            print(f"[trace] span.end {name}", file=sys.stderr)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
