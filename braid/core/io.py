"""Atomic filesystem helpers (write to temp + rename)."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import BinaryIO


def atomicwrite(path: str | os.PathLike, data: bytes) -> None:
    """Write ``data`` to ``path`` atomically.

    Args:
        path: destination path.
        data: payload bytes.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb",
        dir=str(target.parent),
        prefix=target.name + ".",
        suffix=".tmp",
        delete=False,
    ) as fh:
        fh.write(data)
        tmpname = fh.name
    os.replace(tmpname, str(target))


def checksum(path: str | os.PathLike, *, algo: str = "sha256") -> str:
    """Compute a checksum for the file at ``path``.

    Args:
        path: file path.
        algo: hash algorithm name. Defaults to ``"sha256"``.

    Returns:
        The hex digest string.
    """
    h = hashlib.new(algo)
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensurechecksum(
    path: str | os.PathLike,
    expected: str,
    *,
    algo: str = "sha256",
) -> bool:
    """Verify the checksum of ``path`` matches ``expected``.

    Args:
        path: file path.
        expected: expected hex digest.
        algo: hash algorithm. Defaults to ``"sha256"``.

    Returns:
        True if the checksum matches.
    """
    return checksum(path, algo=algo) == expected


def readlazy(path: str | os.PathLike) -> BinaryIO:
    """Open ``path`` for lazy binary reading.

    Args:
        path: file path.

    Returns:
        An open file handle (caller must close).
    """
    return open(path, "rb")  # noqa: SIM115 — explicit close is caller responsibility
