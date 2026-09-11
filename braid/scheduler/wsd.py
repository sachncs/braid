"""WSD (warmup-stable-decay) scheduler."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="scheduler", name="wsd")
class wsd:
    """Warmup, stable, then decay."""

    name: str = "wsd"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, warmupsteps: int, totalsteps: int, decayfrac: float = 0.2) -> None:
        self.warmupsteps = warmupsteps
        self.totalsteps = totalsteps
        self.decayfrac = decayfrac

    def create(self, optimizer: Any) -> Any:
        try:
            import torch
            import math
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("pytorch required") from exc

        optimizer.defaults["lr"]
        decsteps = int(self.decayfrac * self.totalsteps)
        decaystart = self.totalsteps - decsteps

        def lrlambda(step: int) -> float:
            if step < self.warmupsteps:
                return step / max(1, self.warmupsteps)
            if step < decaystart:
                return 1.0
            progress = (step - decaystart) / max(1, decsteps)
            cos = 0.5 * (1 + math.cos(math.pi * progress))
            return cos

        return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lrlambda)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
