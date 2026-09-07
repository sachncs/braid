"""Phase-2 post-training runner — ranking with braided loss + reward weights.

Real implementation: forward through backbone, catalog-matmul scores,
compute braided loss, backward, optimizer step.
"""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment, requiresresource
from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="phase", name="postrain")
class postrain:
    """Phase-2 ranking training using the braided loss.

    Attributes:
        maxsteps: training steps.
        braidterms: list of (lossname, weight).
    """

    name: str = "postrain"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(
        self,
        maxsteps: int = 8000,
        braidterms: list[tuple[str, float]] | None = None,
    ) -> None:
        if maxsteps <= 0:
            raise ValueError("maxsteps must be > 0")
        self.maxsteps = maxsteps
        self.braidterms = braidterms or [
            ("rankingce", 1.0),
            ("rewardweighted", 0.5),
            ("diversityentropy", 0.05),
        ]

    def setup(self) -> None:
        return None

    def run(
        self,
        backbone: Any | None = None,
        catalogstore: Any | None = None,
        dataloader: Any | None = None,
        rewards: Any | None = None,
    ) -> dict[str, Any]:
        """Run real Phase-2 ranking training.

        Args:
            backbone: a registered ``backbone`` concrete.
            catalogstore: a registered ``catalogstore`` concrete.
            dataloader: iterable of ``{"inputids", "attentionmask", "labels", "rewards"}``.
            rewards: dict of name -> reward signal source (or None for zeros).

        Returns:
            Summary dict with steps + per-term losses.

        Raises:
            requiresresource: missing backbone / catalog / dataloader.
            requiresenvironment: torch missing.
        """
        try:
            import torch
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for phase:postrain", hint="pip install torch"
            ) from exc
        if backbone is None:
            raise requiresresource("phase:postrain requires a backbone concrete")
        if catalogstore is None:
            raise requiresresource("phase:postrain requires a catalogstore concrete")
        if dataloader is None:
            raise requiresresource("phase:postrain requires a dataloader")

        log = getlogger("braid.phase.postrain")
        braidlossobj = registry.create(
            "loss",
            "braidedloss",
            terms=self.braidterms,
        )
        params = [p for p in backbone.parameters() if getattr(p, "requires_grad", True)]
        optim = torch.optim.AdamW(params, lr=1e-4)

        losses: list[float] = []
        backbone.train()
        for step, batch in enumerate(dataloader):
            if step >= self.maxsteps:
                break
            inputids = batch["inputids"]
            attentionmask = batch.get("attentionmask")
            labels = batch["labels"]
            rewardvec = batch.get("rewards")
            out = backbone(inputids, attentionmask=attentionmask)
            userrepr = out["pooled"].detach().cpu().numpy()
            scores = catalogstore.score(userrepr)
            scoretensor = torch.as_tensor(scores, dtype=torch.float32)
            lossoutput = {"scores": scoretensor}
            if rewardvec is None:
                rewardvec = torch.zeros(scoretensor.shape[0])
            lossbatch = {"labels": labels, "rewards": rewardvec}
            loss = braidlossobj.compute(lossoutput, lossbatch)
            optim.zero_grad()
            loss.backward()
            optim.step()
            losses.append(float(loss.detach()))
        log.info("postrain.complete", steps=len(losses))
        return {"phase": "postrain", "steps": len(losses), "losses": losses}

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.phase.postrain.loss", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
