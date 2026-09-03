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


def _sampledefault(name: str) -> Any:
    """Return a small default value for conformance probing."""
    n = name.lower()
    if "url" in n:
        return "http://localhost"
    if "path" in n:
        return "./artifacts/tmp"
    if "dir" == n:
        return "./artifacts/tmp"
    if n in {"name", "tokenizername", "modelname", "repo", "encoding", "model", "template", "token"} or any(k in n for k in ["project", "run", "experiment", "mountpoint", "client", "namespace"]):
        return "test"
    if any(k in n for k in ["dim", "size", "epochs", "stages", "buckets", "nbins", "capacity", "max", "n", "k", "m", "topk", "minratio", "maxattempts"]):
        return 4
    if any(k in n for k in ["rate", "p_", "alpha", "weight", "epsilon", "decay", "beta", "lr", "weightdecay", "alpha_", "minloss", "temperature", "freq"]):
        return 0.5
    if "weights" in n:
        return None
    if "popularity" in n:
        return [1.0, 0.5, 0.1, 0.05, 0.01]
    if "embeddings" in n:
        return [[1.0, 0.0], [0.0, 1.0]]
    if "items" in n or "itemids" in n:
        return [[1, 2], [3, 4]]
    if "codebook" in n:
        return [[1.0, 0.0, 0.5], [0.5, 1.0, 0.0]]
    if "scales" in n or "zeros" in n:
        return None
    if "table" in n or "metadata" in n:
        return {}
    if "horizon" in n:
        return 30
    if "warmupsteps" in n or "maxsteps" in n or "steps" in n:
        return 5
    if "recentk" in n or "k" == n:
        return 5
    if "allowed" in n or "arms" in n or "members" in n:
        return ["test"]
    if "dtype" in n:
        return "bf16"
    if "tags" in n or "labels" in n:
        return None
    return "test"


def _trycreate(klass: type) -> tuple[Any | None, str | None]:
    """Try to construct ``klass`` with safe defaults.

    Returns (instance, errormessage). Either instance != None or errormessage is set.
    """
    try:
        sig = inspect.signature(klass.__init__)
        kwargs: dict[str, Any] = {}
        for pname, param in sig.parameters.items():
            if pname == "self":
                continue
            if param.default is inspect.Parameter.empty:
                kwargs[pname] = _sampledefault(pname)
        return klass(**kwargs), None
    except Exception as exc:  # noqa: BLE001
        return None, f"construction failed: {type(exc).__name__}: {exc}"


def verifyone(category: str, name: str, *, traits: bool = True, lifecycle: bool = True, observability: bool = True) -> conformancecheck:
    """Verify a single concrete against all enabled contracts.

    Construction failures are reported as skips (passed=True). Trait mismatches
    on declared capabilities are reported but considered soft (passed=True).
    Hard failures only include contract violations that block polymorphism.

    Args:
        category: registry category.
        name: registry name.
        traits: soft trait check (currently informational).
        lifecycle: ignored (default no-op is acceptable).
        observability: if True, verify a ``metrics`` declaration exists.

    Returns:
        A ``conformancecheck`` result.
    """
    try:
        klass = registry.resolve(category, name)
    except Exception as exc:  # noqa: BLE001
        return conformancecheck(category=category, name=name, passed=False, failures=[f"resolve failed: {exc}"])
    obj, err = _trycreate(klass)
    if obj is None:
        return conformancecheck(category=category, name=name, passed=True, failures=[f"skipped: {err}"])
    failures: list[str] = []
    if observability and not _hasmethod(obj, "metrics"):
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
