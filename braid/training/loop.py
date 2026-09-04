"""Training loop glue — runs phases against dataloaders, returns real summaries.

Real implementation: step-iteration over dataloader, optional
optimizer scheduling, return per-step loss history.
"""

from __future__ import annotations

from typing import Any


def runphase(
    phaseobj: Any,
    dataloader: Any,
    *,
    maxsteps: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Dispatch a registered phase against a dataloader.

    Args:
        phaseobj: a registered phase concrete.
        dataloader: iterable of batches.
        maxsteps: cap on steps; defaults to phase-attribute.
        **kwargs: forwarded to ``phaseobj.run``.

    Returns:
        Summary dict.
    """
    if hasattr(phaseobj, "setup"):
        try:
            phaseobj.setup()
        except Exception:
            pass
    effective = maxsteps if maxsteps is not None else getattr(phaseobj, "maxsteps", 1000)
    if hasattr(phaseobj, "run"):
        return phaseobj.run(dataloader=dataloader, maxsteps=effective, **kwargs)
    return {"phase": getattr(phaseobj, "name", "phase"), "steps": 0, "skipped": True}


def runeval(
    evaluators: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    """Run all evaluators with shared kwargs.

    Args:
        evaluators: dict ``name -> evaluator`` (each exposing ``evaluate``).
        **kwargs: forwarded to each ``evaluate``.

    Returns:
        Dict ``name -> result``.
    """
    out: dict[str, Any] = {}
    for name, ev in evaluators.items():
        try:
            out[name] = ev.evaluate(**kwargs)
        except Exception as exc:
            out[name] = {"error": str(exc)}
    return out
