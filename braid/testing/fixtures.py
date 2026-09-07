"""Tiny synthetic fixtures for tests."""

from __future__ import annotations

import numpy as np


def tinycatalog(numitems: int = 1000, dim: int = 64, seed: int = 0) -> np.ndarray:
    """Return a normalized random catalog embedding matrix.

    Args:
        numitems: number of items. Defaults to 1000.
        dim: embedding dim. Defaults to 64.
        seed: RNG seed. Defaults to 0.

    Returns:
        A ``[numitems, dim]`` float32 array.
    """
    rng = np.random.default_rng(seed)
    e = rng.standard_normal((numitems, dim)).astype(np.float32)
    e /= np.linalg.norm(e, axis=1, keepdims=True) + 1e-8
    return e


def tinyevents(n: int = 100, seed: int = 0) -> list[dict]:
    """Return a list of synthetic engagement events.

    Args:
        n: number of events. Defaults to 100.
        seed: RNG seed. Defaults to 0.

    Returns:
        A list of dicts with keys ``userid``, ``itemid``, ``kind``, ``timestamp``.
    """
    rng = np.random.default_rng(seed)
    return [
        {
            "userid": int(rng.integers(0, 10)),
            "itemid": int(rng.integers(0, 1000)),
            "kind": "play",
            "timestamp": float(i),
        }
        for i in range(n)
    ]


def tinyprompts(n: int = 5) -> list[str]:
    """Return a list of canned prompt templates.

    Args:
        n: number of templates.

    Returns:
        A list of short strings.
    """
    base = [
        "user {u} recently watched {i} and rated {r}",
        "based on history {h}, recommend items",
        "given preferences {p}, suggest the next watch",
    ]
    return (base * (n // len(base) + 1))[:n]
