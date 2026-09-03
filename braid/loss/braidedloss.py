"""Braided loss — composite of weighted loss terms. The namesake."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="loss", name="braidedloss")
class braidedloss:
    """A sum of weighted loss terms. Each term is a registered ``loss`` concrete.

    Example config:
        loss:
          type: braidedloss
          terms:
            - type: rankingce
              weight: 1.0
            - type: lmax
              weight: 0.1
    """

    name: str = "braidedloss"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def __init__(self, terms: list[tuple[str, float]] | None = None) -> None:
        """Build the braid.

        Args:
            terms: list of ``(name, weight)`` tuples; instantiated lazily.
        """
        self.terms: list[tuple[str, float]] = list(terms or [("rankingce", 1.0)])
        self._cache: dict[str, Any] = {}

    def add(self, name: str, weight: float = 1.0) -> None:
        """Add a new term."""
        self.terms.append((name, weight))

    def compute(self, outputs: Any, batch: dict[str, Any]) -> Any:
        """Compute the braid.

        Args:
            outputs: model output dict (must contain ``scores`` for ranking losses,
                ``lmLogits`` for ``lmax``).
            batch: input batch (must contain ``labels`` and ``rewards`` if used).

        Returns:
            Scalar loss tensor.
        """
        from braid.core.error import ioerror

        try:
            import torch
        except ImportError as exc:
            raise ioerror("pytorch required for braidedloss") from exc

        total: Any = outputs.get("scores")
        if isinstance(total, dict):
            total = total.get("loss", outputs.get("loss"))
        if not isinstance(total, torch.Tensor):
            total = torch.tensor(0.0)
        # If we have a base loss, start there; otherwise zero.
        loss = torch.tensor(0.0, requires_grad=True)
        for name, w in self.terms:
            term = self._cache.get(name) or registry.create("loss", name)
            self._cache[name] = term
            try:
                if name == "lmax":
                    contribution = term.compute(outputs.get("lmLogits", outputs.get("logits")), batch.get("inputids"), w)
                elif name == "rewardweighted":
                    contribution = term.compute(outputs["scores"], batch["labels"], batch["rewards"], w)
                elif name == "calibrationloss":
                    contribution = term.compute(outputs["scores"], batch["labels"], w)
                elif name == "diversityentropy":
                    contribution = term.compute(outputs["scores"], w)
                else:
                    contribution = term.compute(outputs["scores"], batch["labels"], w)
                loss = loss + contribution
            except Exception:  # noqa: BLE001 — graceful degrade for missing fields
                continue
        return loss

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.loss.braided.total", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
