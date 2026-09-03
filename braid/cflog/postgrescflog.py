"""Postgres counterfactual logger."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="cflog", name="postgrescflog")
class postgrescflog:
    """Counterfactual log to Postgres."""

    name: str = "postgrescflog"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"persistable", "async", "observable"})

    def __init__(self, url: str, table: str = "cflog") -> None:
        self.url = url
        self.table = table

    def log(self, entry: dict[str, Any]) -> None:
        """Insert an entry asynchronously; failures are swallowed."""
        import json
        try:
            import psycopg
        except ImportError:
            return
        try:
            with psycopg.connect(self.url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"INSERT INTO {self.table} (data, ts) VALUES (%s, NOW())",
                        (json.dumps(entry, default=str),),
                    )
                conn.commit()
        except Exception:  # noqa: BLE001
            return

    def flush(self) -> None:
        return None

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
