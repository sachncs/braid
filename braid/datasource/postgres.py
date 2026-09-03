"""Postgres datasource.

Reads rows from a SQL ``SELECT`` and yields dicts.
"""

from __future__ import annotations

from typing import Any, Iterator

from braid.core.registry import registry


@registry.register(category="datasource", name="postgres")
class postgres:
    """Reads rows from a Postgres table.

    Attributes:
        url: SQLAlchemy/psycopg URL.
        table: table name.
        columns: columns to select.
    """

    name: str = "postgres"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"streamable", "async", "observable"})

    def __init__(self, url: str, table: str, columns: str = "*") -> None:
        """Initialize the Postgres source.

        Args:
            url: postgres connection URL.
            table: table to read.
            columns: column list (default ``"*"``).
        """
        self.url = url
        self.table = table
        self.columns = columns
        self._rows: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        try:
            import psycopg
        except ImportError:
            return
        try:
            with psycopg.connect(self.url) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT {self.columns} FROM {self.table}")
                    cols = [d.name for d in cur.description] if cur.description else []
                    for row in cur.fetchall():
                        self._rows.append(dict(zip(cols, row)))
        except Exception:  # noqa: BLE001 — degraded mode
            return

    def read(self) -> Iterator[dict[str, Any]]:
        yield from iter(self._rows)

    async def aread(self) -> Any:
        try:
            import asyncpg
        except ImportError:
            return list(self.read())
        try:
            conn = await asyncpg.connect(self.url)
        except Exception:
            return list(self.read())
        try:
            rows = await conn.fetch(f"SELECT {self.columns} FROM {self.table}")
        finally:
            await conn.close()
        return [dict(r) for r in rows]

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.datasource.postgres.rows", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
