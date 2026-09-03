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
        self._rows: list[dict[str, Any]] = []
        self._filecount = 0

    def log(self, entry: dict[str, Any]) -> None:
        """Append a log entry; rotate when full."""
        self._rows.append(entry)
        if len(self._rows) >= self.maxperfile:
            self._flush()

    def _flush(self) -> None:
        if not self._rows:
            return
        self._filecount += 1
        path = self.dir / f"cf-{self._filecount:08d}.parquet"
        tbl = pa.Table.from_pylist(self._rows)
        pq.write_table(tbl, str(path))
        self._rows = []

    def flush(self) -> None:
        self._flush()

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
