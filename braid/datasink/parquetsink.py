"""Parquet datasink."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pyarrow as pa
import pyarrow.parquet as pq

from braid.core.registry import registry


@registry.register(category="datasink", name="parquetsink")
class parquetsink:
    """Writes a stream of dicts to a Parquet file.

    Attributes:
        path: output file path.
        schema: optional pyarrow schema.
    """

    name: str = "parquetsink"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, path: str, schema: pa.Schema | None = None) -> None:
        self.path = Path(path)
        self.schema = schema

    def write(self, rows: Iterable[dict[str, Any]]) -> int:
        """Write ``rows`` and return count.

        Args:
            rows: any iterable of dicts.

        Returns:
            Number of rows written.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = list(rows)
        if not data:
            return 0
        tbl = pa.Table.from_pylist(data, schema=self.schema)
        pq.write_table(tbl, str(self.path))
        return len(data)

    async def awrite(self, rows: Iterable[dict[str, Any]]) -> int:
        return self.write(rows)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
