"""Every-N-steps checkpoint."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from braid.core.registry import registry


@registry.register(category="checkpoint", name="everyn")
class everyn:
    """Save every N steps with rotation."""

    name: str = "everyn"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"persistable", "observable"})

    def __init__(self, dir: str, n: int = 1000, maxkeep: int = 5) -> None:
        self.dir = Path(dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.n = n
        self.maxkeep = maxkeep

    def shouldsave(self, step: int) -> bool:
        return step > 0 and step % self.n == 0

    def pathfor(self, step: int) -> str:
        return str(self.dir / f"step{step}.pt")

    def rotate(self) -> None:
        """Delete old checkpoints beyond ``maxkeep``."""
        candidates = sorted(self.dir.glob("step*.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in candidates[self.maxkeep :]:
            try:
                old.unlink()
            except Exception:  # noqa: BLE001
                continue

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
