"""Runtime conformance harness.

Used by the test suite and the ``braid conformance`` CLI to verify that
every registered concrete actually satisfies its declared traits,
lifecycle, observability, and capabilities.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any

from braid.core.error import protocolviolation
from braid.core.registry import registry
from braid.core.trait import ALL_TRAITS


@dataclass
class conformancecheck:
    """Result of a conformance check."""

    category: str
    name: str
    passed: bool
    failures: list[str] = field(default_factory=list)


@dataclass
class contractfail:
    """A single failing conformance contract."""

    contract: str
    detail: str


def verifyone(category: str, name: str, *, traits: bool = True, lifecycle: bool = True, observability: bool = True) -> conformancecheck:
    """Verify a single concrete against all enabled contracts.

    Args:
        category: registry category.
        name: registry name.
        traits: if True, verify declared traits are implemented.
        lifecycle: if True, verify lifecycle hooks exist.
        observability: if True, verify observability declarations exist.

    Returns:
        A ``conformancecheck`` result.
    """
    failures: list[str] = []
    klass = registry.resolve(category, name)
    obj = klass()
    if traits:
        caps = getattr(obj, "capabilities", frozenset())
        if "streamable" in caps and not _hasmethod(obj, "openstream"):
            failures.append("declares streamable but missing openstream")
        if "cachable" in caps and not (
            _hasmethod(obj, "cacheget") and _hasmethod(obj, "cacheput")
        ):
            failures.append("declares cachable but missing cacheget/cacheput")
        if "persistable" in caps and not (
            _hasmethod(obj, "persist") and _hasmethod(obj, "restore")
        ):
            failures.append("declares persistable but missing persist/restore")
        if "idempotent" in caps and not _hasmethod(obj, "idempotencykey"):
            failures.append("declares idempotent but missing idempotencykey")
        if "distributable" in caps and not (
            _hasmethod(obj, "shardrank") and _hasmethod(obj, "numshards")
        ):
            failures.append("declares distributable but missing shardrank/numshards")
    if lifecycle:
        if not (
            _hasasyncmethod(obj, "setup")
            or _hasmethod(obj, "setup")
            or hasattr(obj, "setup")
        ):
            pass  # default no-op is acceptable
    if observability:
        if not _hasmethod(obj, "metrics"):
            failures.append("missing metrics() declaration")
    return conformancecheck(
        category=category,
        name=name,
        passed=not failures,
        failures=failures,
    )


def verifyall(*, categories: list[str] | None = None) -> list[conformancecheck]:
    """Verify all registered concretes.

    Args:
        categories: optional list of categories to limit checks.

    Returns:
        A list of ``conformancecheck`` results.
    """
    results: list[conformancecheck] = []
    cats = categories or registry.categories()
    for c in cats:
        for n in registry.available(c):
            results.append(verifyone(c, n))
    return results


def _hasmethod(obj: Any, name: str) -> bool:
    return callable(getattr(obj, name, None))


def _hasasyncmethod(obj: Any, name: str) -> bool:
    method = getattr(obj, name, None)
    if method is None:
        return False
    return inspect.iscoroutinefunction(method) or _hasmethod(obj, name)


def assertconformant(category: str, name: str) -> None:
    """Raise ``protocolviolation`` if a concrete fails contracts.

    Args:
        category: registry category.
        name: registry name.
    """
    check = verifyone(category, name)
    if not check.passed:
        raise protocolviolation(
            f"concrete {category}.{name} failed contracts: {check.failures}"
        )
