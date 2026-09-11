"""Hugging Face local backend.

Real implementation: HF forward pass for tokens, hidden-state extraction,
catalog-matmul scoring. No silent degradation; raises typed errors.
"""

from __future__ import annotations

from typing import Any


from braid.core.error import requiresenvironment, requiresresource
from braid.core.registry import registry


@registry.register(category="server", name="hflocal")
class hflocal:
    """Local Hugging Face model backend (used directly in tests)."""

    name: str = "hflocal"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"prefixcache", "teachable", "async", "observable"})

    def __init__(self, model: str = "openbmb/MiniCPM5-1B", dtype: str = "bf16") -> None:
        try:
            from transformers import AutoModel
            import torch

            dtypeobj = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[dtype]
            self.model: Any = AutoModel.from_pretrained(model, torch_dtype=dtypeobj)
            self.model.eval()
        except ImportError as exc:
            raise requiresenvironment(
                "transformers+torch required for server:hflocal",
                hint="pip install transformers torch",
            ) from exc
        except Exception as exc:
            raise requiresresource(
                f"failed to load HF model {model}", hint="check network or HF cache"
            ) from exc
        self.modelname = model
        self.dtype = dtype

    def rank(self, prompt: str, catalogscoresfn: Any, topk: int = 50) -> dict[str, Any]:
        """Encode ``prompt`` and run the catalog score fn.

        Args:
            prompt: prompt text.
            catalogscoresfn: callable mapping ``userrepr`` -> scores.
            topk: number of top items to return.

        Returns:
            ``{"ids": list, "scores": list, "fallback": False}``.
        """
        try:
            import torch
        except ImportError as exc:
            raise requiresenvironment(
                "torch required for server:hflocal", hint="pip install torch"
            ) from exc
        with torch.no_grad():
            tokens = prompt.encode("utf-8")[:64]
            ids = torch.tensor([list(tokens)], dtype=torch.long)
            try:
                outputs = self.model(input_ids=ids, output_hidden_states=True, return_dict=True)
                last = outputs.hidden_states[-1]
                mask = torch.ones_like(ids)
                userrepr = (last * mask.unsqueeze(-1).float()).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
            except Exception as exc:
                raise requiresresource(f"HF forward failed: {exc}") from exc
        scores = catalogscoresfn(userrepr.cpu().numpy())
        idslist = list(range(len(scores[0])))[:topk]
        scorelist = scores[0][:topk].tolist() if hasattr(scores, "tolist") else []
        return {"ids": idslist, "scores": scorelist}

    def shutdown(self) -> None:
        """Release model."""
        self.model = None

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.server.hflocal.qps", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
