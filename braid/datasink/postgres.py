"""Postgres datasink."""

from __future__ import annotations

from typing import Any, Iterable

from braid.core.registry import registry


@registry.register(category="datasink", name="postgres")
class postgres:
    """Insert rows into a Postgres table via COPY."""

    name: str = "postgres"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, url: str, table: str) -> None:
        self.url = url
        self.table = table

    def write(self, rows: Iterable[dict[str, Any]]) -> int:
        """Insert via executemany.

        Returns:
            Number of rows written.
        """
        rows = list(rows)
        if not rows:
            return 0
        try:
            import psycopg
        except ImportError:
            return 0
        cols = list(rows[0].keys())
        placeholders = ",".join(["%s"] * len(cols))
        sql = f"INSERT INTO {self.table} ({','.join(cols)}) VALUES ({placeholders})"
        with psycopg.connect(self.url) as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, [tuple(r[c] for c in cols) for r in rows])
            conn.commit()
        return len(rows)

    async def awrite(self, rows: Iterable[dict[str, Any]]) -> int:
        rows = list(rows)
        try:
            import asyncpg
        except ImportError:
            return self.write(rows)
        conn = await asyncpg.connect(self.url)
        try:
            cols = list(rows[0].keys())
            placeholders = ",".join([f"${i+1}" for i in range(len(cols))])
            sql = f"INSERT INTO {self.table} ({','.join(cols)}) VALUES ({placeholders})"
            await conn.executemany(sql, [tuple(r[c] for c in cols) for r in rows])
        finally:
            await conn.close()
        return len(rows)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
