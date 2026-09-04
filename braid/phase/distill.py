"""Distillation phase — KL divergence between teacher and student logits.

Real implementation: forward through both backbones, KL loss.
"""

from __future__ import annotations

from typing import Any

from braid.core.error import requiresenvironment, requiresresource
from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="phase", name="distill")
class distill:
    """Distillation phase with KL-divergence loss."""

    name: str = "distill"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, teacher: str = "minicpm5", student: str = "pythia1", temperature: float = 2.0) -> None:
        if not 0 < temperature:
            raise ValueError("temperature must be > 0")
        self.teacher = teacher
        self.student = student
        self.temperature = temperature

    def setup(self) -> None:
        return None

    def run(self, dataloader: Any | None = None, maxsteps: int = 1000) -> dict[str, Any]:
        """Distill teacher into student via KL divergence.

        Args:
            dataloader: iterable of token batches.
            maxsteps: cap on training steps.

        Returns:
            Summary dict.

        Raises:
            requiresresource: backbones/dataloader missing.
            requiresenvironment: torch missing.
        """
        try:
            import torch
            import torch.nn.functional as F
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for phase:distill", hint="pip install torch"
            ) from exc
        try:
            teacher = registry.create("backbone", self.teacher)
        except Exception as exc:
            raise requiresresource(f"failed to create teacher backbone: {exc}") from exc
        try:
            student = registry.create("backbone", self.student)
        except Exception as exc:
            raise requiresresource(f"failed to create student backbone: {exc}") from exc
        if dataloader is None:
            raise requiresresource("phase:distill requires a dataloader")
        params = [p for p in student.parameters() if getattr(p, "requires_grad", True)]
        optim = torch.optim.AdamW(params, lr=1e-4)
        losses: list[float] = []
        student.train()
        teacher.eval()
        for step, batch in enumerate(dataloader):
            if step >= maxsteps:
                break
            inputids = batch["inputids"]
            with torch.no_grad():
                tout = teacher(inputids, attentionmask=batch.get("attentionmask"))
                tlogits = tout["hiddens"]
            sout = student(inputids, attentionmask=batch.get("attentionmask"))
            slogits = sout["hiddens"]
            t = self.temperature
            loss = F.kl_div(
                F.log_softmax(slogits / t, dim=-1),
                F.softmax(tlogits / t, dim=-1),
                reduction="batchmean",
            ) * (t * t)
            optim.zero_grad()
            loss.backward()
            optim.step()
            losses.append(float(loss.detach()))
        getlogger("braid.phase.distill").info("distill.complete", steps=len(losses))
        return {"phase": "distill", "steps": len(losses), "losses": losses}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
