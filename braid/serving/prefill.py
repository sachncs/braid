"""vLLM-style prefill-only hidden-state extraction."""

from __future__ import annotations

from typing import Any


def extractpooled(hiddenstates: Any, attentionmask: Any | None = None) -> Any:
    """Return the pooled representation from the last layer's hidden states.

    Args:
        hiddenstates: ``[batch, seqlen, dim]`` tensor.
        attentionmask: ``[batch, seqlen]`` mask.

    Returns:
        ``[batch, dim]`` pooled tensor.
    """
    try:
        import torch

        if attentionmask is None:
            return hiddenstates[:, -1, :]
        mask = attentionmask.unsqueeze(-1).float()
        return (hiddenstates * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
    except Exception:  # noqa: BLE001
        return hiddenstates
