"""Aim tracker integration.

Requires the ``aim`` package (pip install aim).
"""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="tracker", name="aim")
class aim:
    """Aim experiment tracker backed by ``aim``."""

    name: str = "aim"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "observable"})

    def __init__(self, dir: str = "./artifacts/aim", run: str | None = None) -> None:
        try:
            from aim import Run

            self.dir = dir
            self.run = run or "default"
            self.runobj: Any = Run(repo=self.dir, experiment=self.run)
        except ImportError as exc:
            raise requiresenvironment(
                "aim is required for tracker:aim", hint="pip install aim"
            ) from exc

    def log(self, key: str, value: float, step: int | None = None) -> None:
        try:
            self.runobj.track(value, name=key, step=step or 0)
        except Exception:
            pass

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
