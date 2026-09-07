"""Deterministic seeding utilities."""

from __future__ import annotations

import os
import random

import numpy as np


def seedall(seed: int = 0) -> dict[str, int]:
    """Seed all common RNG sources and return the per-source seed used.

    Args:
        seed: master seed.

    Returns:
        A dict mapping RNG source name to the actual seed used.

    Example:
        >>> seeds = seedall(42)
        >>> seeds["python"]
        42
    """
    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    pyseed = seed
    npseed = seed + 1
    torchseed = seed + 2
    random.seed(pyseed)
    np.random.seed(npseed)
    try:
        import torch
    except ImportError:
        torch = None  # type: ignore[assignment]
    if torch is not None:
        torch.manual_seed(torchseed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(torchseed + 1)
    return {"python": pyseed, "numpy": npseed, "torch": torchseed}
