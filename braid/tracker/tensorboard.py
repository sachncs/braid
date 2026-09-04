"""TensorBoard tracker."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="tracker", name="tensorboard")
class tensorboard:
    """TensorBoard tracker via torch.utils.tensorboard."""

    name: str = "tensorboard"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "observable"})

    def __init__(self, dir: str = "./artifacts/tb", run: str = "default") -> None:
        self.dir = dir
        self.runname = run
        self.writer: Any | None = None

    def init(self) -> None:
        try:
            from torch.utils.tensorboard import SummaryWriter

            self.writer = SummaryWriter(log_dir=f"{self.dir}/{self.runname}")
        except Exception:  # noqa: BLE001
            self.writer = None

    def log(self, key: str, value: float, step: int | None = None) -> None:
        if self.writer is None:
            self.init()
        if self.writer is not None:
            try:
                self.writer.add_scalar(key, value, step or 0)
            except Exception:  # noqa: BLE001
                pass

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
