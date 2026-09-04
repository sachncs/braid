"""Llama 3.2 3B Instruct backbone wrapper. Real HF-backed."""

from __future__ import annotations

from typing import Any

import torch

from braid.core.error import requiresenvironment, requiresresource
from braid.core.registry import registry


@registry.register(category="backbone", name="llama32")
class llama32:
    """Llama 3.2 3B Instruct backbone."""

    name: str = "llama32"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"gpu", "fusedkernel", "async", "teachable"})

    def __init__(self, size: str = "3B", dtype: str = "bf16", gradientcheckpointing: bool = True) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            repo = "meta-llama/Llama-3.2-3B-Instruct"
            self._tok = AutoTokenizer.from_pretrained(repo)
            dtypeobj = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[dtype]
            self._model = AutoModelForCausalLM.from_pretrained(repo, torch_dtype=dtypeobj)
        except ImportError as exc:
            raise requiresenvironment(
                "transformers+torch are required for backbone:llama32",
                hint="pip install transformers torch",
            ) from exc
        except Exception as exc:
            raise requiresresource(
                "failed to load Llama-3.2-3B-Instruct from HF Hub",
                hint="accept Meta license at https://llama.meta.com and re-export HF_TOKEN",
            ) from exc
        self.size = size
        self.dtype = dtype
        self.gradientcheckpointing = gradientcheckpointing
        if gradientcheckpointing:
            try:
                self._model.gradient_checkpointing_enable()
            except Exception:
                pass

    def encode(self, inputids: Any, attentionmask: Any | None = None) -> Any:
        """Run encoder; return hidden states + pooled vector."""
        out = self._model(
            input_ids=inputids,
            attention_mask=attentionmask,
            output_hidden_states=True,
            return_dict=True,
        )
        last = out.hidden_states[-1]
        if attentionmask is not None:
            mask = attentionmask.unsqueeze(-1).float()
            pooled = (last * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
        else:
            pooled = last.mean(dim=1)
        return {"hiddens": last, "pooled": pooled}

    def tok(self, text: str) -> Any:
        """Tokenize ``text`` via the bundled tokenizer."""
        return self._tok(text, return_tensors="pt")

    @property
    def hiddendim(self) -> int:
        return int(self._model.config.hidden_size)

    def teachexamples(self) -> list[str]:
        return ["Q: hi\nA: hello!"]

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
