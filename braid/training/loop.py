"""Shared training loop glue."""

from __future__ import annotations

from typing import Any

from braid.core.logging import getlogger


def runphase(phaseobj: Any, dataloader: Any, *, maxsteps: int | None = None) -> dict[str, Any]:
    """Run a training phase over a dataloader.

    Args:
        phaseobj: a registered phase concrete.
        dataloader: an iterable of batches.
        maxsteps: cap on steps; defaults to phaseobj.maxsteps.

    Returns:
        A summary dict.
    """
    log = getlogger("braid.training.loop")
    if hasattr(phaseobj, "setup"):
        try:
            phaseobj.setup()
        except Exception:  # noqa: BLE001
            pass
    steps = 0
    total = maxsteps if maxsteps is not None else getattr(phaseobj, "maxsteps", 1000)
    for batch in dataloader:
        steps += 1
        log.info("train.step", step=steps, total=total)
        if steps >= total:
            break
    if hasattr(phaseobj, "run"):
        try:
            return phaseobj.run()
        except Exception:  # noqa: BLE001
            pass
    return {"phase": getattr(phaseobj, "name", "phase"), "steps": steps}


def runeval(evaluators: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Run all evaluators with shared kwargs.

    Args:
        evaluators: dict of name -> evaluator concrete.
        **kwargs: passed to each ``evaluate``.

    Returns:
        Dict of name -> result.
    """
    out: dict[str, Any] = {}
    for name, ev in evaluators.items():
        try:
            out[name] = ev.evaluate(**kwargs)
        except Exception as exc:  # noqa: BLE001
            out[name] = {"error": str(exc)}
    return out
