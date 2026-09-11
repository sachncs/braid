"""Re-rank a response with a custom scoring function."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="resppost", name="rerank")
class rerank:
    """Re-rank top-k results with a custom function."""

    name: str = "rerank"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable"})

    def process(self, response: dict[str, Any], scorer: Any | None = None) -> dict[str, Any]:
        """Rerank ``response`` using ``scorer`` if provided; else identity."""
        ids = response.get("ids", [])
        response.get("scores", [])
        if scorer is None or not ids:
            return response
        custom = [scorer(int(i)) for i in ids]
        order = sorted(range(len(ids)), key=lambda j: custom[j], reverse=True)
        return {
            "ids": [ids[j] for j in order],
            "scores": [custom[j] for j in order],
        }

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
