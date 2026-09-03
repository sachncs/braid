"""Weights & Biases tracker."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="tracker", name="wandb")
class wandb:
    """Weights & Biases tracker."""

    name: str = "wandb"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "observable"})

    def __init__(self, project: str = "braid", run: str = "default") -> None:
        self.project = project
        self.runname = run
        self._run: Any | None = None

    def init(self) -> None:
        try:
            import wandb

            self._run = wandb.init(project=self.project, name=self.runname, reinit=True)
        except Exception:  # noqa: BLE001
            self._run = None

    def log(self, key: str, value: float, step: int | None = None) -> None:
        if self._run is None:
            self.init()
        if self._run is not None:
            try:
                self._run.log({key: value}, step=step)
            except Exception:  # noqa: BLE001
                pass

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
