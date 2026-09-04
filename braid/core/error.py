"""Typed error model with retry classification.

All braid errors descend from ``braiderror``. Errors carry a category,
retryability, and optionally suggested fixes.
"""

from __future__ import annotations

from typing import Any


class braiderror(Exception):
    """Base for all braid errors.

    Attributes:
        category: coarse error category (config, registry, validation, ...).
        retryable: whether callers should retry the operation.
        hint: optional human-readable fix suggestion.
        context: arbitrary structured metadata.
    """

    category: str = "internal"
    retryable: bool = False

    def __init__(
        self,
        message: str,
        *,
        available: list[str] | None = None,
        hint: str | None = None,
        retryable: bool | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.available = available or []
        self.hint = hint
        if retryable is not None:
            self.retryable = retryable
        self.context = context or {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.message!r})"


class configurationerror(braiderror):
    """Raised when a config is invalid or fails validation."""

    category = "config"
    retryable = False


class registryerror(braiderror):
    """Raised when a registry lookup fails."""

    category = "registry"
    retryable = False

    def __init__(self, message: str, *, available: list[str] | None = None, **kw: Any) -> None:
        super().__init__(message, available=available, **kw)
        if available:
            self.hint = f"available: {', '.join(available)}"


class validationerror(braiderror):
    """Raised on value-shape or semantics failures."""

    category = "validation"
    retryable = False


class protocolviolation(braiderror):
    """Raised when a concrete fails a Protocol contract."""

    category = "protocol"
    retryable = False


class ioerror(braiderror):
    """Raised on filesystem/network I/O failures."""

    category = "io"
    retryable = True


class concurrencyerror(braiderror):
    """Raised when concurrent execution violates an invariant."""

    category = "concurrency"
    retryable = True


class resourceerror(braiderror):
    """Raised on out-of-memory, GPU, or quota errors."""

    category = "resource"
    retryable = True


class requiresenvironment(braiderror):
    """Raised when a concrete needs an external resource that is missing.

    Use this for unavailable services / packages / drivers. The error
    message should describe the missing dependency and how to install it.
    """

    category = "environment"
    retryable = False


class requiresresource(braiderror):
    """Raised when a concrete needs a runtime resource that's unavailable.

    Examples: a model weight file, a config file, a network endpoint.
    """

    category = "resource-missing"
    retryable = False


class retrystrategy:
    """Polymorphic retry policy.

    Concrete: ``exponential``, ``constant``, ``linearbackoff``, ``fibered``, ``none``.
    """

    def __init__(self, maxattempts: int = 5, base: float = 0.5, cap: float = 30.0) -> None:
        self.maxattempts = maxattempts
        self.base = base
        self.cap = cap

    def delay(self, attempt: int) -> float:
        """Seconds to wait before retry ``attempt`` (1-indexed)."""
        if attempt < 1:
            return 0.0
        return min(self.cap, self.base * (2 ** (attempt - 1)))

    def shouldretry(self, attempt: int, exc: braiderror) -> bool:
        return attempt < self.maxattempts and exc.retryable
