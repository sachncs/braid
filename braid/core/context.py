"""Request context propagated through every layer."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass
class requestcontext:
    """Polymorphic request context.

    Attributes:
        requestid: unique identifier for the request.
        traceparent: W3C traceparent header, or ``None``.
        userid: principal user id, or ``None``.
        deadline: wall-clock deadline.
        principal: auth principal, or ``None``.
        ratelimitbudget: tokens remaining for rate limiting.
        featureflags: per-flag boolean overrides.
        experimentid: experiment id (for A/B routing), or ``None``.
        experimentarm: assigned arm, or ``None``.
        metadata: arbitrary structured data.
    """

    requestid: str = field(default_factory=lambda: str(uuid.uuid4()))
    traceparent: str | None = None
    userid: str | None = None
    deadline: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(seconds=30)
    )
    principal: str | None = None
    ratelimitbudget: int = 1
    featureflags: dict[str, bool] = field(default_factory=dict)
    experimentid: str | None = None
    experimentarm: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def child(self) -> "requestcontext":
        """Return a derived context for a sub-call.

        The new context inherits principal, experiment, and flags but
        allocates a fresh request id.
        """
        return requestcontext(
            traceparent=self.traceparent,
            userid=self.userid,
            deadline=self.deadline,
            principal=self.principal,
            ratelimitbudget=self.ratelimitbudget,
            featureflags=dict(self.featureflags),
            experimentid=self.experimentid,
            experimentarm=self.experimentarm,
            metadata=dict(self.metadata),
        )

    def withdeadline(self, seconds: float) -> "requestcontext":
        """Return a copy with a deadline ``seconds`` from now."""
        ctx = self.child()
        ctx.deadline = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        return ctx

    def withflag(self, key: str, value: bool) -> "requestcontext":
        """Return a copy with ``key`` set in featureflags."""
        ctx = self.child()
        ctx.featureflags[key] = value
        return ctx

    def hasflag(self, key: str) -> bool:
        return self.featureflags.get(key, False)

    def timebudget(self) -> float:
        """Seconds remaining until deadline (negative if past)."""
        delta = self.deadline - datetime.now(timezone.utc)
        return delta.total_seconds()

    def toheaders(self) -> dict[str, str]:
        """Serialize to HTTP header values."""
        out: dict[str, str] = {"x-braid-request-id": self.requestid}
        if self.traceparent:
            out["traceparent"] = self.traceparent
        if self.userid:
            out["x-braid-user-id"] = self.userid
        if self.experimentid:
            out["x-braid-experiment-id"] = self.experimentid
            if self.experimentarm:
                out["x-braid-experiment-arm"] = self.experimentarm
        return out
