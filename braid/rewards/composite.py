"""Composite reward — weighted sum of registered rewards.

Implements the same callable contract as any individual reward so it
can be substituted transparently.
"""

from __future__ import annotations

import inspect
from typing import Any

from braid.core.error import requiresenvironment, requiresresource
from braid.core.registry import registry


@registry.register(category="reward", name="composite")
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

    def resolve(self, name: str) -> Any:
        """Instantiate a reward concrete by registry name.

        Args:
            name: registered reward name.

        Returns:
            An instantiated concrete.

        Raises:
            requiresenvironment: if the reward is not registered.
        """
        if name in self.instances:
            return self.instances[name]
        try:
            inst = registry.create("reward", name)
        except Exception as exc:
            raise requiresenvironment(
                f"reward '{name}' not registered",
                hint="register the reward concrete via @registry.register('reward', name=...)",
                cause=str(exc),
            ) from exc
        self.instances[name] = inst
        return inst

    def score(self, event: dict[str, Any], ctx: dict[str, Any] | None = None) -> float:
        """Return the weighted sum of component scores.

        Uses ``inspect.signature`` to route ``history`` from ``ctx`` to
        reward concretes that accept it (e.g., ``diversitybonus``).

        Args:
            event: the candidate event.
            ctx: optional context dict (may carry ``history``).

        Returns:
            Float in ``[0, 1]``.

        Raises:
            requiresresource: if all components fail and there is nothing to combine.
        """
        try:
            import torch
        except ImportError:
            torch = None  # noqa: F841 — torch is optional for some rewards
        total = 0.0
        wsum = 0.0
        failures: dict[str, str] = {}
        for name, w in self.members:
            try:
                comp = self.resolve(name)
                sig = inspect.signature(comp.score)
                kwargs: dict[str, Any] = {}
                if "history" in sig.parameters and ctx is not None:
                    kwargs["history"] = ctx.get("history", ctx if isinstance(ctx, list) else [])
                val = comp.score(event, **kwargs)
                if torch is not None and isinstance(val, torch.Tensor):
                    val = float(val.detach().item())
                total += w * float(val)
                wsum += abs(w)
            except Exception as exc:  # noqa: BLE001
                failures[name] = str(exc)
        if wsum == 0:
            raise requiresresource(
                "no rewards produced a score",
                hint="check registered reward signatures",
                cause=str(failures),
            )
        self.lastfailures = failures
        return total / wsum

    def observability(self) -> dict[str, Any]:
        return {
            "metrics": [
                {"name": "braid.reward.composite.score", "type": "gauge"},
            ]
        }

    def metrics(self) -> list[Any]:
        return []
