"""Lifecycle Protocol — uniform setup/warmup/shutdown/health on every concrete.

Every concrete registered with braid is wrapped in a ``lifecycledelegate``
at construction time, which guarantees all four hooks exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable

from braid.core.context import requestcontext


@dataclass
class healthstatus:
    """Result of a lifecycle health probe.

    Attributes:
        status: live, degraded, or dead.
        details: free-form key/value details.
        dependencies: per-dependency status (kafka -> "live", redis -> "degraded", ...).
    """

    status: Literal["live", "degraded", "dead"]
    details: dict[str, Any] = field(default_factory=dict)
    dependencies: dict[str, str] = field(default_factory=dict)

    def islive(self) -> bool:
        return self.status == "live"

    def merge(self, other: "healthstatus") -> "healthstatus":
        if self.status == "dead" or other.status == "dead":
            status = "dead"
        elif self.status == "degraded" or other.status == "degraded":
            status = "degraded"
        else:
            status = "live"
        return healthstatus(
            status=status,
            details={**self.details, **other.details},
            dependencies={**self.dependencies, **other.dependencies},
        )


@runtime_checkable
class lifecycle(Protocol):
    """Lifecycle hooks every concrete implements.

    All hooks receive a ``requestcontext``. ``setup`` is mandatory; the
    others are no-op by default.
    """

    async def setup(self, ctx: requestcontext) -> None: ...

    async def warmup(self, ctx: requestcontext) -> None: ...

    async def shutdown(self, ctx: requestcontext) -> None: ...

    async def health(self, ctx: requestcontext) -> healthstatus: ...


class lifecycledelegate:
    """Wraps a concrete, providing no-op defaults for missing lifecycle hooks."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner

    async def setup(self, ctx: requestcontext) -> None:
        if hasattr(self.inner, "setup"):
            await self.inner.setup(ctx)

    async def warmup(self, ctx: requestcontext) -> None:
        if hasattr(self.inner, "warmup"):
            await self.inner.warmup(ctx)

    async def shutdown(self, ctx: requestcontext) -> None:
        if hasattr(self.inner, "shutdown"):
            await self.inner.shutdown(ctx)

    async def health(self, ctx: requestcontext) -> healthstatus:
        if hasattr(self.inner, "health"):
            return await self.inner.health(ctx)
        return healthstatus(status="live", details={"delegate": True})
