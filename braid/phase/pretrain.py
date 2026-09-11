"""Phase-1 continued pretraining runner.

Real implementation: forward/backward/optimizer/scheduler loop on a
language-model backbone. Caller must inject a backbone concrete and a
dataloader.
"""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment, requiresresource
from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="phase", name="pretrain")
class pretrain:
    """Continued pretraining phase.

    Attributes:
        maxsteps: training steps.
        lr: learning rate.
    """

    name: str = "pretrain"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, maxsteps: int = 5000, lr: float = 1e-4) -> None:
        if maxsteps <= 0 or lr <= 0:
            raise ValueError("maxsteps and lr must be > 0")
        self.maxsteps = maxsteps
        self.lr = lr

    def setup(self) -> None:
        """No-op at construction; wired externally by training loop."""
        return None

    def run(
        self,
        backbone: Any | None = None,
        dataloader: Any | None = None,
        optimizer: Any | None = None,
        scheduler: Any | None = None,
    ) -> dict[str, Any]:
        """Run real LM continued pretraining.

        Args:
            backbone: registered ``backbone`` concrete.
            dataloader: iterable of ``{"inputids", "attentionmask", "labels"}``.
            optimizer: torch optimizer over backbone parameters.
            scheduler: torch LR scheduler.

        Returns:
            Summary dict with steps + final loss.

        Raises:
            requiresenvironment: if torch is missing.
            requiresresource: if backbone/dataloader are missing.
        """
        try:
            import torch
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for phase:pretrain", hint="pip install torch"
            ) from exc
        if backbone is None:
            raise requiresresource("phase:pretrain requires a backbone concrete")
        if dataloader is None:
            raise requiresresource("phase:pretrain requires a dataloader")
        if optimizer is None:
            params = [p for p in backbone.parameters() if getattr(p, "requires_grad", True)]
            optimizer = torch.optim.AdamW(params, lr=self.lr)

        log = getlogger("braid.phase.pretrain")
        losses: list[float] = []
        backbone.train()
        for step, batch in enumerate(dataloader):
            if step >= self.maxsteps:
                break
            inputids = batch["inputids"]
            attentionmask = batch.get("attentionmask")
            labels = batch.get("labels")
            out = backbone(inputids, attentionmask=attentionmask)
            logits = out["hiddens"]
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = (
                labels[..., 1:].contiguous()
                if labels is not None
                else inputids[..., 1:].contiguous()
            )
            try:
                import torch.nn.functional as F

                loss = F.cross_entropy(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1),
                    ignore_index=-100,
                )
            except Exception as exc:
                raise requiresresource(f"pretrain loss failed: {exc}") from exc
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            if scheduler is not None:
                scheduler.step()
            losses.append(float(loss.detach()))
        log.info("pretrain.complete", steps=len(losses), lastloss=losses[-1] if losses else None)
        return {"phase": "pretrain", "steps": len(losses), "losses": losses}

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.phase.pretrain.loss", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
