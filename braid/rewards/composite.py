"""Composite reward over a weighted list of registered rewards.

Implements the same Protocol so any reward can be substituted.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


class compositereward:
    """Weighted sum of reward components.

    Attributes:
        members: list of (name, weight) pairs.
    """

    name: str = "compositereward"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, members: list[tuple[str, float]] | None = None) -> None:
        if members is None:
            members = [("longtermreturn", 1.0), ("diversitybonus", 0.3)]
        self.members = list(members)
        self.cache: dict[str, Any] = {}
        for n, _ in self.members:
            if n not in self.cache:
                self.cache[n] = registry.create("reward", n)

    def add(self, name: str, weight: float) -> None:
        """Add a member; instantiated lazily."""
        if name not in self.cache:
            self.cache[name] = registry.create("reward", name)
        self.members.append((name, weight))

    def score(self, event: dict[str, Any], ctx: dict[str, Any] | None = None) -> float:
        """Return the weighted sum of component scores."""
        total = 0.0
        wsum = 0.0
        for name, w in self.members:
            reward = self.cache.get(name) or registry.create("reward", name)
            self.cache[name] = reward
            try:
                import inspect

                sig = inspect.signature(reward.score)
                kwargs: dict[str, Any] = {}
                if "history" in sig.parameters and ctx is not None:
                    kwargs["history"] = ctx.get("history", ctx if isinstance(ctx, list) else [])
                score = reward.score(event, **kwargs) if hasattr(reward, "score") else 0.0
            except Exception:  # noqa: BLE001
                score = 0.0
            total += w * score
            wsum += abs(w)
        return total / wsum if wsum else 0.0

    def weights(self) -> dict[str, float]:
        return dict(self.members)

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return "reward:composite:v1"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
