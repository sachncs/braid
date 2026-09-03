"""EMA (exponential moving average) checkpoint strategy."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from braid.core.registry import registry


@registry.register(category="checkpoint", name="ema")
class ema:
    """EMA-averaged weights over the training run."""

    name: str = "ema"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"persistable", "observable", })

    def __init__(self, dir: str, decay: float = 0.999) -> None:
        self.dir = Path(dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.decay = decay
        self._shadow: dict[str, Any] = {}

    def update(self, modelparams: dict[str, Any]) -> None:
        """Update shadow params with EMA."""
        for k, v in modelparams.items():
            if k not in self._shadow:
                self._shadow[k] = v.detach().clone()
            else:
                self._shadow[k].mul_(self.decay).add_(v.detach(), alpha=1.0 - self.decay)

    def shadowcopy(self) -> dict[str, Any]:
        return {k: v.detach().clone() for k, v in self._shadow.items()}

    def saveshape(self, step: int) -> str:
        return str(self.dir / f"ema-step{step}.pt")

    def persist(self, path: str) -> None:
        """Serialize shadow tensors via torch.save if available, else skip."""
        try:
            import torch

            torch.save(self._shadow, path)
        except Exception:  # noqa: BLE001
            pass

    def restore(self, path: str) -> None:
        try:
            import torch

            self._shadow = torch.load(path)
        except Exception:  # noqa: BLE001
            self._shadow = {}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
