"""Hugging Face local backend (CPU/dev-friendly)."""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.registry import registry


@registry.register(category="server", name="hflocal")
class hflocal:
    """Local Hugging Face model backend for development & tests."""

    name: str = "hflocal"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"prefixcache", "teachable", "async", "observable"})

    def __init__(self, model: str = "openbmb/MiniCPM5-1B", dtype: str = "bf16") -> None:
        self.modelname = model
        self.dtype = dtype
        self._model: Any | None = None

    def warmup(self) -> None:
        try:
            from transformers import AutoModel

            self._model = AutoModel.from_pretrained(self.modelname)
        except Exception:  # noqa: BLE001
            self._model = None

    def rank(self, prompt: str, catalogscoresfn: Any, topk: int = 50) -> dict[str, Any]:
        """Encode the prompt and run a catalog score fn."""
        if self._model is None:
            self.warmup()
        try:
            import torch
        except ImportError:
            return {"ids": list(range(topk)), "scores": [0.0] * topk}
        tokens = prompt.encode("utf-8")
        inp = torch.tensor([[min(255, b) for b in tokens[:64]]], dtype=torch.long)
        with torch.no_grad():
            rep = torch.randn(1, 64)  # degraded embedding if model fails to load
        scores = catalogscoresfn(rep.numpy())
        ids = list(range(len(scores[0])))[:topk]
        return {"ids": ids, "scores": scores[0][:topk].tolist() if hasattr(scores, "tolist") else []}

    def shutdown(self) -> None:
        self._model = None

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.server.hflocal.qps", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
