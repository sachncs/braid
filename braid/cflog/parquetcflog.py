"""Parquet counterfactual logger."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from braid.core.registry import registry


@registry.register(category="cflog", name="parquetcflog")
class parquetcflog:
    """Counterfactual log to rotating Parquet files."""

    name: str = "parquetcflog"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"persistable", "async", "observable"})

    def __init__(self, dir: str = "artifacts/cf", maxperfile: int = 1000) -> None:
        self.dir = Path(dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.maxperfile = maxperfile
        self.rows: list[dict[str, Any]] = []
        self.filecount = 0

    def log(self, entry: dict[str, Any]) -> None:
        """Append a log entry; rotate when full."""
        self.rows.append(entry)
        if len(self.rows) >= self.maxperfile:
            self.flush()

    def flush(self) -> None:
        if not self.rows:
            return
        self.filecount += 1
        path = self.dir / f"cf-{self.filecount:08d}.parquet"
        tbl = pa.Table.from_pylist(self.rows)
        pq.write_table(tbl, str(path))
        self.rows = []

    def flush(self) -> None:
        self.flush()

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
