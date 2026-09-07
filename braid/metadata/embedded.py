"""Embedded metadata provider.

Holds metadata in-memory; useful when metadata is computed rather than
fetched from an external source.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="metadata", name="embedded")
class embedded:
    """An in-memory metadata table keyed by item id."""

    name: str = "embedded"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "persistable", "observable"})

    def __init__(self, table: dict[int | str, dict] | None = None) -> None:
        self.table: dict = dict(table or {})

    def get(self, itemid: int | str) -> dict:
        return self.table.get(itemid, {})

    def put(self, itemid: int | str, meta: dict) -> None:
        self.table[itemid] = meta

    def cacheget(self, key: int | str) -> dict | None:
        return self.table.get(key)

    def cacheput(self, key: int | str, value: dict) -> None:
        self.table[key] = value

    def cacheinvalidate(self, key: int | str) -> None:
        self.table.pop(key, None)

    def persist(self, path: str) -> None:
        """Write as JSON."""
        import json
        from pathlib import Path

        Path(path).write_text(json.dumps(self.table, default=str))

    def restore(self, path: str) -> None:
        import json
        from pathlib import Path

        if not Path(path).exists():
            return
        raw = json.loads(Path(path).read_text())
        self.table = {int(k) if k.isdigit() else k: v for k, v in raw.items()}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
