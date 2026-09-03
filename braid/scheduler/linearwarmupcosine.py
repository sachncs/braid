"""Linear warmup + cosine decay."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="scheduler", name="linearwarmupcosine")
class linearwarmupcosine:
    """Linear warmup followed by cosine decay."""

    name: str = "linearwarmupcosine"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, warmupsteps: int, maxsteps: int, minratio: float = 0.1) -> None:
        self.warmupsteps = warmupsteps
        self.maxsteps = maxsteps
        self.minratio = minratio

    def create(self, optimizer: Any) -> Any:
        try:
            import torch
            import math
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("pytorch required") from exc

        baselr = optimizer.defaults["lr"]

        def lrlambda(step: int) -> float:
            if step < self.warmupsteps:
                return step / max(1, self.warmupsteps)
            progress = (step - self.warmupsteps) / max(1, self.maxsteps - self.warmupsteps)
            progress = min(1.0, max(0.0, progress))
            cos = 0.5 * (1 + math.cos(math.pi * progress))
            return self.minratio + (1 - self.minratio) * cos

        return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lrlambda)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
