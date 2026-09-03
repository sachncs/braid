"""Local parquet datasource.

Reads row-groups from a local parquet directory as a stream of dicts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from braid.core.registry import registry


@registry.register(category="datasource", name="localparquet")
class localparquet:
    """Reads local Parquet files row-by-row.

    Attributes:
        path: directory containing ``.parquet`` files.

    Example:
        >>> src = localparquet(path="data/processed")
        >>> for row in src.read():
        ...     print(row)
    """

    name: str = "localparquet"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"streamable", "async", "persistable", "observable"})

    def __init__(self, path: str) -> None:
        """Initialize the source.

        Args:
            path: directory with parquet files.

        Raises:
            FileNotFoundError: if the path does not exist.
        """
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"datasource path not found: {path}")
        self._index = 0
        self._rows: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        try:
            import pyarrow.parquet as pq
        except ImportError:
            self._rows = []
            return
        rows: list[dict[str, Any]] = []
        for f in sorted(self.path.glob("*.parquet")):
            try:
                table = pq.read_table(str(f))
                rows.extend(table.to_pylist())
            except Exception:  # noqa: BLE001 — degraded mode
                continue
        self._rows = rows

    def read(self) -> Iterator[dict[str, Any]]:
        """Yield rows from the source.

        Yields:
            Each row as a dict.
        """
        yield from iter(self._rows)

    async def aread(self) -> Any:
        """Async read (returns the full list; subclasses may override)."""
        return list(self.read())

    def openstream(self) -> Iterator[dict[str, Any]]:
        return self.read()

    def persist(self, path: str) -> None:
        """No-op: local files are the source-of-truth."""
        return None

    def restore(self, path: str) -> None:
        """Reload from ``path``."""
        self.path = Path(path)
        self._index = 0
        self._load()

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"localparquet:{self.path}"

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.datasource.rows", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
