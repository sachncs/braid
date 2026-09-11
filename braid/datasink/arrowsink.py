"""Arrow IPC sink."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pyarrow as pa
import pyarrow.ipc as pi

from braid.core.registry import registry


@registry.register(category="datasink", name="arrowsink")
class arrowsink:
    """Writes Arrow IPC (feather) format.

    Attributes:
        path: directory under which ``rows.arrow`` is written.
    """

    name: str = "arrowsink"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def write(self, rows: Iterable[dict[str, Any]]) -> int:
        """Write ``rows`` to ``path/rows.arrow`` and return count.

        ``path`` is treated as a directory so callers (notably ``ingest``)
        can pass one sink per split and avoid per-call file naming.
        """
        self.path.mkdir(parents=True, exist_ok=True)
        data = list(rows)
        if not data:
            return 0
        tbl = pa.Table.from_pylist(data)
        outfile = self.path / "rows.arrow"
        with open(outfile, "wb") as fh:
            with pi.new_stream(fh, tbl.schema) as writer:
                writer.write_table(tbl)
        return len(data)

    async def awrite(self, rows: Iterable[dict[str, Any]]) -> int:
        return self.write(rows)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
