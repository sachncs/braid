"""Catalog scoring glue for serving."""

from __future__ import annotations

from typing import Any

import numpy as np


def scoresfromcatalog(
    userrepr: np.ndarray, catalogstore: Any, ids: np.ndarray | None = None
) -> np.ndarray:
    """Compute scores for ``userrepr`` against the catalog store.

    Args:
        userrepr: ``[batch, dim]`` representation.
        catalogstore: a registered ``catalogstore`` concrete.
        ids: optional subset of item ids.

    Returns:
        ``[batch, len(ids)|numitems]`` score array.
    """
    return catalogstore.score(userrepr, ids)


def toparray(x: Any) -> np.ndarray:
    """Convert to numpy array if needed."""
    if hasattr(x, "detach"):
        return x.detach().cpu().numpy()
    if isinstance(x, np.ndarray):
        return x
    return np.asarray(x)
