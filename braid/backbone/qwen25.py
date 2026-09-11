"""Qwen 2.5 1.5B Instruct backbone. Real HF-backed."""

from __future__ import annotations

from typing import Any


from braid.core.error import requiresenvironment, requiresresource
from braid.core.registry import registry


@registry.register(category="backbone", name="qwen25")
class qwen25:
    """Qwen 2.5 1.5B Instruct backbone."""

    name: str = "qwen25"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"gpu", "fusedkernel", "async", "teachable"})

    def __init__(
        self, size: str = "1.5B", dtype: str = "bf16", gradientcheckpointing: bool = True
    ) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            repo = "Qwen/Qwen2.5-1.5B-Instruct"
            self.tok = AutoTokenizer.from_pretrained(repo)
            dtypeobj = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[dtype]
            self.model = AutoModelForCausalLM.from_pretrained(repo, torch_dtype=dtypeobj)
        except ImportError as exc:
            raise requiresenvironment(
                "transformers+torch are required for backbone:qwen25",
                hint="pip install transformers torch",
            ) from exc
        except Exception as exc:
            raise requiresresource(
                "failed to load Qwen2.5-1.5B-Instruct from HF Hub",
                hint="check network and disk",
            ) from exc
        self.size = size
        self.dtype = dtype
        self.gradientcheckpointing = gradientcheckpointing
        if gradientcheckpointing:
            try:
                self.model.gradient_checkpointing_enable()
            except Exception:
                pass

    def encode(self, inputids: Any, attentionmask: Any | None = None) -> Any:
        """Run encoder; return hidden states + pooled vector."""
        out = self.model(
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
        """Tokenize ``text``."""
        return self.tok(text, return_tensors="pt")

    @property
    def hiddendim(self) -> int:
        return int(self.model.config.hidden_size)

    def teachexamples(self) -> list[str]:
        return ["Q: 1+1?\nA: 2"]

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
