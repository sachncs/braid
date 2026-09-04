"""TensorBoard tracker. Requires ``torch``."""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="tracker", name="tensorboard")
class tensorboard:
    """TensorBoard tracker via ``torch.utils.tensorboard``."""

    name: str = "tensorboard"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "observable"})

    def __init__(self, dir: str = "./artifacts/tb", run: str = "default") -> None:
        try:
            from torch.utils.tensorboard import SummaryWriter

            self.dir = dir
            self.runname = run
            self.writer: Any = SummaryWriter(log_dir=f"{self.dir}/{self.runname}")
        except ImportError as exc:
            raise requiresenvironment(
                "torch is required for tracker:tensorboard",
                hint="pip install torch tensorboard",
            ) from exc

    def log(self, key: str, value: float, step: int | None = None) -> None:
        try:
            self.writer.add_scalar(key, value, step or 0)
        except Exception:
            pass

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
