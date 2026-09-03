"""Latest checkpoint strategy."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from braid.core.registry import registry


@registry.register(category="checkpoint", name="latest")
class latest:
    """Always overwrite the latest checkpoint."""

    name: str = "latest"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"persistable", "observable"})

    def __init__(self, dir: str) -> None:
        self.dir = Path(dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.latestpath = str(self.dir / "latest.pt")

    def shouldsave(self, step: int) -> bool:
        return True

    def pathfor(self, step: int) -> str:
        return self.latestpath

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
