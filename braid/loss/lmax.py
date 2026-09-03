"""Auxiliary language-modeling loss over verbalized text."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="loss", name="lmax")
class lmax:
    """Auxiliary next-token LM loss over verbalized prompts and metadata."""

    name: str = "lmax"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def compute(self, lmLogits: Any, labels: Any, weight: float = 1.0) -> Any:
        try:
            import torch
            import torch.nn.functional as F

            shift_logits = lmLogits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
            )
            return weight * loss
        except Exception as exc:  # noqa: BLE001
            from braid.core.error import ioerror

            raise ioerror("pytorch required for lmax") from exc

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.loss.lmax", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
