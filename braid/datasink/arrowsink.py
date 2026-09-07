"""Arrow IPC sink."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pyarrow as pa
import pyarrow.ipc as pi

from braid.core.registry import registry


@registry.register(category="datasink", name="arrowsink")
class arrowsink:
    """Writes Arrow IPC (feather) format."""

    name: str = "arrowsink"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def write(self, rows: Iterable[dict[str, Any]]) -> int:
        """Write ``rows`` to IPC and return count."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = list(rows)
        if not data:
            return 0
        tbl = pa.Table.from_pylist(data)
        with open(self.path, "wb") as fh:
            with pi.new_stream(fh, tbl.schema) as writer:
                writer.write_table(tbl)
        return len(data)

    async def awrite(self, rows: Iterable[dict[str, Any]]) -> int:
        return self.write(rows)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
