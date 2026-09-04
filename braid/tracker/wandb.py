"""Weights & Biases tracker. Requires ``wandb``."""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="tracker", name="wandb")
class wandb:
    """Weights & Biases tracker."""

    name: str = "wandb"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "observable"})

    def __init__(self, project: str = "braid", run: str = "default") -> None:
        try:
            import wandb

            self.project = project
            self.runname = run
            self.runobj: Any = wandb.init(project=self.project, name=self.runname, reinit=True)
        except ImportError as exc:
            raise requiresenvironment(
                "wandb is required for tracker:wandb", hint="pip install wandb"
            ) from exc

    def log(self, key: str, value: float, step: int | None = None) -> None:
        try:
            self.runobj.log({key: value}, step=step)
        except Exception:
            pass

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
