"""Composite reward — weighted sum of registered rewards.

Implements the same callable contract as any individual reward so it
can be substituted transparently.
"""

from __future__ import annotations

import inspect
from typing import Any

from braid.core.registry import registry


class compositereward:
    """Weighted sum of registered reward concretes.

    Attributes:
        members: list of ``(name, weight)`` pairs.
        instances: cached concrete instances keyed by name.
    """

    name: str = "compositereward"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, members: list[tuple[str, float]] | None = None) -> None:
        if members is None:
            members = [("longtermreturn", 1.0), ("diversitybonus", 0.3)]
        self.members = list(members)
        self.instances: dict[str, Any] = {}

    def add(self, name: str, weight: float = 1.0) -> None:
        """Add a reward component (lazy-instantiated on demand)."""
        if name not in self.instances:
            self.instances[name] = registry.create("reward", name)
        self.members.append((name, weight))

    def _resolve(self, name: str) -> Any:
        """Instantiate a reward concrete by registry name."""
        if name not in self.instances:
            self.instances[name] = registry.create("reward", name)
        return self.instances[name]

    def score(self, event: dict[str, Any], ctx: dict[str, Any] | None = None) -> float:
        """Return the weighted sum of component scores.

        Uses ``inspect.signature`` to route ``history`` from ``ctx`` to
        reward concretes that accept it (e.g., ``diversitybonus``).

        Args:
            event: the candidate event.
            ctx: optional context dict (may carry ``history``).

        Returns:
            Float in ``[0, 1]``.
        """
        total = 0.0
        wsum = 0.0
        for name, w in self.members:
            comp = self._resolve(name)
            try:
                sig = inspect.signature(comp.score)
                kwargs: dict[str, Any] = {}
                if "history" in sig.parameters and ctx is not None:
                    kwargs["history"] = ctx.get("history", ctx if isinstance(ctx, list) else [])
                total += w * comp.score(event, **kwargs)
            except Exception:
                continue
            wsum += abs(w)
        return total / wsum if wsum else 0.0

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
