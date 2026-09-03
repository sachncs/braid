"""Reward-weighted ranking loss.

Weights each example by a scalar reward (e.g., long-term-return + diversity).
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="loss", name="rewardweighted")
class rewardweighted:
    """Reward-weighted cross-entropy over an engagement."""

    name: str = "rewardweighted"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, normalize: bool = True) -> None:
        self.normalize = normalize

    def compute(self, scores: Any, labels: Any, rewards: Any, weight: float = 1.0) -> Any:
        """Reward-weighted cross-entropy.

        Args:
            scores: ``[batch, numitems]`` logits.
            labels: ``[batch]`` labels.
            rewards: ``[batch]`` per-example reward scalars.
            weight: scalar multiplier on the loss.

        Returns:
            Scalar tensor.
        """
        try:
            import torch
            import torch.nn.functional as F
        except ImportError as exc:
            from braid.core.error import ioerror

            raise ioerror("pytorch required for rewardweighted") from exc
        losses = F.cross_entropy(scores, labels, reduction="none")
        rw = rewards.float() if hasattr(rewards, "float") else rewards
        if self.normalize:
            rw = rw / (rw.abs().sum() + 1e-8) * len(rw)
        per = losses * rw
        return weight * per.mean()

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
