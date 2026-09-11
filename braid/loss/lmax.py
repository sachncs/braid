"""Auxiliary LM loss over verbalized text."""

from __future__ import annotations

from typing import Any

import torch.nn.functional as F

from braid.core.registry import registry


@registry.register(category="loss", name="lmax")
class lmax:
    """Auxiliary next-token LM loss over verbalized prompts/metadata."""

    name: str = "lmax"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self) -> None:
        """No parameters."""

    def compute(self, lmlogits: Any, labels: Any, weight: float = 1.0) -> Any:
        """Compute auxiliary LM loss.

        Args:
            lmlogits: ``[batch, seqlen, vocab]`` logits.
            labels: ``[batch, seqlen]`` token ids; ``-100`` ignored.
            weight: scalar multiplier.
        """
        shift_logits = lmlogits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        loss = F.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
            ignore_index=-100,
        )
        return weight * loss

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.loss.lmax", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
