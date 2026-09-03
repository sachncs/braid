"""S3 parquet datasource (lazy import to avoid boto3 dep when unused)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from braid.core.error import ioerror
from braid.core.registry import registry


@registry.register(category="datasource", name="s3parquet")
class s3parquet:
    """Reads Parquet files from S3.

    Attributes:
        bucket: the S3 bucket.
        prefix: key prefix.
        region: AWS region.
    """

    name: str = "s3parquet"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"streamable", "async", "persistable", "observable"})

    def __init__(self, bucket: str, prefix: str = "", region: str = "us-east-1") -> None:
        """Initialize the S3 source.

        Args:
            bucket: S3 bucket name.
            prefix: optional key prefix.
            region: AWS region string.
        """
        self.bucket = bucket
        self.prefix = prefix
        self.region = region
        self._rows: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        try:
            import s3fs
        except ImportError as exc:
            from braid.core.logging import getlogger

            getlogger("braid.datasource.s3parquet").warning(
                "s3fs missing; s3parquet will yield empty stream",
                extra={"error": str(exc)},
            )
            return
        fs = s3fs.S3FileSystem(region=self.region)
        glob = f"{self.bucket}/{self.prefix}*.parquet"
        paths = fs.glob(glob)
        if not paths:
            return
        try:
            import pyarrow.parquet as pq
        except ImportError:
            return
        for p in paths:
            try:
                tbl = pq.read_table(p, filesystem=fs)
                self._rows.extend(tbl.to_pylist())
            except Exception:
                continue

    def read(self) -> Iterator[dict[str, Any]]:
        yield from iter(self._rows)

    async def aread(self) -> Any:
        return list(self.read())

    def openstream(self) -> Iterator[dict[str, Any]]:
        return self.read()

    def persist(self, path: str) -> None:
        return None

    def restore(self, path: str) -> None:
        bucket, _, prefix = path.partition("/")
        self.bucket = bucket
        self.prefix = prefix
        self._rows = []
        self._load()

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.datasource.s3.bytes", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
