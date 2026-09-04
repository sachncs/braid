"""Aim tracker integration."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="tracker", name="aim")
class aim:
    """Aim experiment tracker."""

    name: str = "aim"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "observable"})

    def __init__(self, dir: str = "./artifacts/aim", run: str | None = None) -> None:
        self.dir = dir
        self.run = run or "default"
        self.run: Any | None = None

    def init(self) -> None:
        try:
            from aim import Run

            self.run = Run(repo=self.dir, experiment=self.run)
        except Exception:  # noqa: BLE001 — degraded mode
            self.run = None

    def log(self, key: str, value: float, step: int | None = None) -> None:
        if self.run is None:
            self.init()
        if self.run is not None:
            try:
                self.run.track(value, name=key, step=step or 0)
            except Exception:  # noqa: BLE001
                pass

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
