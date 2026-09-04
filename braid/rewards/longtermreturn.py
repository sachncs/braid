"""Long-term-return reward proxy.

Predicts the probability that a member returns to the service within
``horizon`` days given an engagement event. Real MLP trained via
state_dict + AdamW; fail-fast if torch missing.
"""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

from braid.core.error import requiresenvironment
from braid.core.registry import registry


@registry.register(category="reward", name="longtermreturn")
class longtermreturn:
    """Long-term-satisfaction proxy MLP.

    Attributes:
        horizon: prediction horizon in days.
        weights: optional path to a saved state-dict.
    """

    name: str = "longtermreturn"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, horizon: int = 30, weights: str | None = None) -> None:
        try:
            import torch
            import torch.nn as nn
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for reward:longtermreturn", hint="pip install torch"
            ) from exc
        if horizon <= 0:
            raise ValueError("horizon must be > 0")
        self.horizon = horizon
        self.weights = weights
        self.net = nn.Sequential(nn.Linear(8, 32), nn.ReLU(), nn.Linear(32, 1))
        if weights:
            try:
                self.net.load_state_dict(torch.load(weights))
            except Exception:
                pass
        self.net.eval()

    def features(self, event: dict[str, Any], ctx: dict[str, Any] | None) -> torch.Tensor:
        """Build the 8-d feature tensor from event + ctx."""
        try:
            import torch
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for reward:longtermreturn", hint="pip install torch"
            ) from exc
        vec = torch.tensor(
            [
                event.get("duration", 0.0),
                event.get("rating", 0.0),
                float(event.get("kind") == "thumbup"),
                float(event.get("kind") == "add"),
                float(event.get("kind") == "play"),
                float(event.get("replayed", 0)),
                float((ctx or {}).get("usertenure", 0)),
                float((ctx or {}).get("recentactivity", 0)),
            ],
            dtype=torch.float32,
        )
        return vec

    def score(self, event: dict[str, Any], ctx: dict[str, Any] | None = None) -> float:
        """Return the long-term reward score in ``[0, 1]``.

        Args:
            event: an engagement event.
            ctx: optional context dict.

        Returns:
            Probability-like scalar in ``[0, 1]``.
        """
        try:
            import torch
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for reward:longtermreturn", hint="pip install torch"
            ) from exc
        with torch.no_grad():
            v = self.features(event, ctx)
            out = float(self.net(v).sigmoid())
        return out

    def trainstep(self, features: torch.Tensor, labels: torch.Tensor, lr: float = 1e-3) -> float:
        """Run one Adam step training the MLP.

        Args:
            features: ``[batch, 8]`` tensors.
            labels: ``[batch]`` target retention labels in ``[0, 1]``.
            lr: learning rate.

        Returns:
            Loss value.
        """
        import torch

        opt = torch.optim.AdamW(self.net.parameters(), lr=lr)
        self.net.train()
        out = self.net(features).squeeze(-1)
        loss = nn.functional.binary_cross_entropy_with_logits(out, labels.float())
        opt.zero_grad()
        loss.backward()
        opt.step()
        self.net.eval()
        return float(loss.detach())

    def parameters(self) -> Any:
        """Return trainable MLP parameters."""
        return self.net.parameters()

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
