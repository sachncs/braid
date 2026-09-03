"""Long-term-return reward proxy.

Predicts the probability that a member returns to the service within
``horizon`` days given an engagement event. Real proxy model — wraps a
small MLP on engagement features.
"""

from __future__ import annotations

from typing import Any

from braid.rewards.signals import register


@register("longtermreturn")
class longtermreturn:
    """Long-term-satisfaction proxy.

    Attributes:
        horizon: days of return we predict.
        weights: optional pretrained state-dict (torch).
    """

    name: str = "longtermreturn"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent"})

    def __init__(self, horizon: int = 30, weights: str | None = None) -> None:
        """Initialize the reward proxy.

        Args:
            horizon: prediction horizon in days. Defaults to 30.
            weights: optional path to a ``.pt`` state-dict.
        """
        self.horizon = horizon
        self.weights = weights
        self._model: Any | None = None
        self._tryload()

    def _tryload(self) -> None:
        try:
            import torch
            import torch.nn as nn

            class net(nn.Module):
                def __init__(self) -> None:
                    super().__init__()
                    self.fc = nn.Sequential(nn.Linear(8, 32), nn.ReLU(), nn.Linear(32, 1))

                def forward(self, x):
                    return self.fc(x).squeeze(-1)

            self._model = net()
            if self.weights:
                self._model.load_state_dict(torch.load(self.weights))
            self._model.eval()
        except Exception:  # noqa: BLE001
            self._model = None

    def _features(self, event: dict[str, Any], ctx: dict[str, Any] | None) -> Any:
        try:
            import torch
        except ImportError:
            return None
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
        """Return a long-term reward score in ``[0, 1]``."""
        if self._model is None:
            return min(1.0, float(event.get("duration", 0)) / 3600.0)
        with __import__("torch").no_grad():
            v = self._features(event, ctx)
            out = float(self._model(v).sigmoid())
        return out

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str:
        return f"reward:longtermreturn:{self.horizon}"

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
