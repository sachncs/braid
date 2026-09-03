"""Elbow-finder CLI for context-length optimization."""

from __future__ import annotations

from typing import Any


def run(events: list[dict[str, Any]], krange: range | None = None) -> dict[int, int]:
    """Sweep history lengths and report signal token counts.

    Args:
        events: full history.
        krange: range of history sizes to try.

    Returns:
        A dict mapping history size to signal count.
    """
    from braid.truncation.signalweighted import signalweighted

    krange = krange or range(5, 105, 5)
    out: dict[int, int] = {}
    for k in krange:
        kept = signalweighted(budget=k).fit(events)
        out[k] = len(kept)
    return out
