"""Best-loss checkpoint strategy."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from braid.core.registry import registry


@registry.register(category="checkpoint", name="best")
class best:
    """Save the checkpoint whose val loss is lowest."""

    name: str = "best"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"persistable", "observable", })

    def __init__(self, dir: str) -> None:
        self.dir = Path(dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.bestloss: float | None = None
        self.bestpath: str | None = None

    def shouldsave(self, step: int, valloss: float) -> bool:
        """Return True iff current is best so far."""
        if self.bestloss is None or valloss < self.bestloss:
            self.bestloss = valloss
            self.bestpath = str(self.dir / f"best-step{step}.pt")
            return True
        return False

    def persist(self, path: str) -> None:
        """Save the bookkeeping."""
        import json

        Path(path).write_text(json.dumps({"bestloss": self.bestloss, "bestpath": self.bestpath}))

    def restore(self, path: str) -> None:
        import json
        from pathlib import Path

        p = Path(path)
        if not p.exists():
            return
        data = json.loads(p.read_text())
        self.bestloss = data.get("bestloss")
        self.bestpath = data.get("bestpath")

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
