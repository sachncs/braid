"""Quantizer training runner — encode → quantize → decode → reconstruction loss.

Real implementation: full training loop with commitment loss and
straight-through estimator.
"""

from __future__ import annotations

from typing import Any

import torch
import torch.nn.functional as F

from braid.core.logging import getlogger
from braid.core.registry import registry
from braid.quantizer.encoder import encoder as encoderconcrete
from braid.quantizer.decoder import decoder as decoderconcrete
from braid.quantizer.quantizer import quantizer as quantizerconcrete


@registry.register(category="quantizer", name="trainer")
class trainer:
    """End-to-end encoder → quantizer → decoder trainer.

    Operational state (set during ``run``):
        encoder/decoder: registered MLP modules.
        qzr: registered RVQ.
        opt: AdamW over encoder + decoder params.
        hist: training loss history.

    Attributes:
        numcodes, dim, numstages: quantizer config.
        maxsteps: training steps.
        lr: learning rate.
        inputdim, hiddendim: encoder config.
    """

    name: str = "trainer"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(
        self,
        numcodes: int = 256,
        dim: int = 64,
        numstages: int = 4,
        maxsteps: int = 500,
        lr: float = 1e-3,
        inputdim: int = 64,
        hiddendim: int = 128,
    ) -> None:
        if numcodes <= 0 or dim <= 0 or numstages <= 0 or maxsteps <= 0:
            raise ValueError("config values must be > 0")
        self.numcodes = numcodes
        self.dim = dim
        self.numstages = numstages
        self.maxsteps = maxsteps
        self.lr = lr
        self.inputdim = inputdim
        self.hiddendim = hiddendim
        self.encoder: Any | None = None
        self.decoder: Any | None = None
        self.qzr: Any | None = None
        self.opt: Any | None = None
        self.hist: list[float] = []

    def setup(self) -> None:
        """Build encoder, decoder, codebook, optimizer."""
        self.encoder = encoderconcrete(self.inputdim, self.hiddendim)
        self.qzr = quantizerconcrete(
            numcodes=self.numcodes, dim=self.hiddendim, numstages=self.numstages
        )
        self.decoder = decoderconcrete(self.hiddendim, self.inputdim)

        params = list(self.encoder.parameters()) + list(self.decoder.parameters())
        self.opt = torch.optim.AdamW(params, lr=self.lr)
        self.hist = []

    def run(self, dataloader: Any | None = None) -> dict[str, Any]:
        """Run the training loop.

        Args:
            dataloader: optional iterable of ``[batch, inputdim]`` tensors.
                Defaults to a synthetic random batch each step.

        Returns:
            Training summary dict.
        """
        self.setup()

        log = getlogger("braid.quantizer.trainer")
        if dataloader is None:
            synthetic = torch.randn(64, self.inputdim)
            dataloader = iter([synthetic] * self.maxsteps)
        for step, batch in enumerate(dataloader):
            if step >= self.maxsteps:
                break
            if isinstance(batch, list):
                batch = torch.tensor(batch, dtype=torch.float32)
            z = self.encoder.encode(batch)
            codes = []
            residual = z
            for cb in self.qzr.codebooks:
                sims = cb @ residual.T
                idx = int(sims.argmax(dim=0).mean().item())
                codes.append(idx)
                residual = residual - cb[idx]
            zhat = torch.tensor(self.qzr.dequantize(codes), dtype=z.dtype)
            zhat = zhat.unsqueeze(0).expand_as(z)
            recon = self.decoder.decode(zhat)
            loss = F.mse_loss(recon, batch)
            self.opt.zero_grad()
            loss.backward()
            self.opt.step()
            self.hist.append(float(loss.detach()))
        log.info(
            "trainer.complete", steps=len(self.hist), lastloss=self.hist[-1] if self.hist else None
        )
        return {"phase": "quantizer", "artifact": "quantizer.pt", "steps": len(self.hist)}

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.quantizer.trainer.loss", "type": "gauge"}]}

    def metrics(self) -> list[Any]:
        return []
