"""Retrain-trigger drift response."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from braid.core.registry import registry
from braid.core.logging import getlogger


@registry.register(category="driftresponse", name="retraintrigger")
class retraintrigger:
    """Write a retrain trigger file when drift is detected."""

    name: str = "retraintrigger"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "persistable"})

    def __init__(self, path: str = "artifacts/retrain.trigger") -> None:
        self.path = Path(path)

    def respond(self, signal: dict[str, Any]) -> None:
        """Write a trigger file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(f"drift={signal.get('score')}\n")
        getlogger("braid.driftresponse.retraintrigger").warning("retrain.triggered", path=str(self.path))

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
