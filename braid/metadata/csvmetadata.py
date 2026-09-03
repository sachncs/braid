"""CSV metadata provider."""

from __future__ import annotations

from pathlib import Path

from braid.core.registry import registry


@registry.register(category="metadata", name="csvmetadata")
class csvmetadata:
    """Load item metadata from a CSV file with an ``itemid`` column."""

    name: str = "csvmetadata"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"cachable", "persistable", "observable"})

    def __init__(self, path: str) -> None:
        """Load metadata eagerly.

        Args:
            path: path to a CSV with an ``itemid`` column.
        """
        self.path = Path(path)
        self._by_id: dict = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        import csv

        with open(self.path, encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if "itemid" not in row:
                    continue
                try:
                    key = int(row["itemid"])
                except ValueError:
                    key = row["itemid"]
                self._by_id[key] = row

    def get(self, itemid: int | str) -> dict:
        """Return metadata for ``itemid`` or empty dict."""
        return self._by_id.get(itemid, {})

    def cacheget(self, key: int | str) -> dict | None:
        return self._by_id.get(key)

    def cacheput(self, key: int | str, value: dict) -> None:
        self._by_id[key] = value

    def cacheinvalidate(self, key: int | str) -> None:
        self._by_id.pop(key, None)

    def persist(self, path: str) -> None:
        """No-op: metadata is read-only."""
        return None

    def restore(self, path: str) -> None:
        self.path = Path(path)
        self._by_id = {}
        self._load()

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
