"""Braided loss — composite of weighted loss terms. The namesake."""

from __future__ import annotations

from typing import Any

from braid.core.error import ioerror, requiresenvironment, requiresresource
from braid.core.registry import registry


@registry.register(category="loss", name="braidedloss")
class braidedloss:
    """A sum of weighted loss terms. Each term is a registered ``loss`` concrete.

    Example config::

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
    capabilities: frozenset[str] = frozenset({"observable"})

    def __init__(self, terms: list[tuple[str, float]] | None = None) -> None:
        """Build the braid.

        Args:
            terms: list of ``(name, weight)`` tuples; instantiated lazily on
                first ``compute`` call.
        """
        self.terms: list[tuple[str, float]] = list(terms or [("rankingce", 1.0)])
        self.cache: dict[str, Any] = {}

    def add(self, name: str, weight: float = 1.0) -> None:
        """Add a new term.

        Args:
            name: registered loss name.
            weight: scalar weight for this term.
        """
        self.terms.append((name, weight))

    def compute(self, outputs: Any, batch: dict[str, Any]) -> Any:
        """Compute the braid.

        Args:
            outputs: model output dict (must contain ``scores`` for ranking losses,
                ``lmLogits`` for ``lmax``).
            batch: input batch (must contain ``labels`` and ``rewards`` if used).

        Returns:
            Scalar loss tensor (requires_grad where applicable).

        Raises:
            requiresenvironment: if torch is not installed.
            requiresresource: if a term is invoked with a missing arg or backend error.
        """
        try:
            import torch
        except ImportError as exc:
            raise requiresenvironment(
                "pytorch required for braidedloss",
                hint="pip install torch",
            ) from exc

        loss = torch.tensor(0.0, requires_grad=True)
        perterm: dict[str, float] = {}
        for name, w in self.terms:
            term = self.cache.get(name) or registry.create("loss", name)
            self.cache[name] = term
            if name == "lmax":
                logits = outputs.get("lmLogits", outputs.get("logits"))
                if logits is None:
                    raise requiresresource(
                        "lmax term requires lmLogits in outputs",
                        hint="call the backbone with output_hidden_states=True",
                    )
                contribution = term.compute(logits, batch.get("inputids"), w)
            elif name == "rewardweighted":
                if "rewards" not in batch:
                    raise requiresresource(
                        "rewardweighted term requires 'rewards' key in batch",
                    )
                contribution = term.compute(outputs["scores"], batch["labels"], batch["rewards"], w)
            elif name == "calibrationloss":
                contribution = term.compute(outputs["scores"], batch["labels"], w)
            elif name == "diversityentropy":
                contribution = term.compute(outputs["scores"], w)
            else:
                if "scores" not in outputs:
                    raise requiresresource(
                        f"term '{name}' requires 'scores' in outputs",
                    )
                contribution = term.compute(outputs["scores"], batch["labels"], w)
            loss = loss + contribution
            perterm[name] = float(contribution.detach().item()) if hasattr(contribution, "detach") else float(contribution)
        self.lastreport = perterm
        return loss

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.loss.braided.total", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
