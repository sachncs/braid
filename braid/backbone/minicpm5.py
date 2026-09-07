"""MiniCPM5 backbone wrapper.

Loads the real MiniCPM-5 1B/2B model from Hugging Face Hub and returns
hidden states + a pooled representation. Fails fast if the model
weights can't be downloaded.
"""

from __future__ import annotations

from typing import Any

import torch

from braid.core.error import requiresenvironment, requiresresource
from braid.core.registry import registry


@registry.register(category="backbone", name="minicpm5")
class minicpm5:
    """MiniCPM5 1B / 2B backbone wrapper.

    Attributes:
        size: model size string (``"1B"`` or ``"2B"``).
        dtype: ``"bf16"``, ``"fp16"``, or ``"fp32"``.
        gradientcheckpointing: bool.
    """

    name: str = "minicpm5"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"gpu", "fusedkernel", "async", "teachable"})

    def __init__(
        self,
        size: str = "1B",
        dtype: str = "bf16",
        gradientcheckpointing: bool = True,
    ) -> None:
        """Initialize. Loads weights; fail-fast on missing resources."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise requiresenvironment(
                "transformers+torch are required for backbone:minicpm5",
                hint="pip install transformers torch",
            ) from exc
        if size not in {"1B", "2B"}:
            raise ValueError(f"size must be 1B or 2B, got {size!r}")
        repo = "openbmb/MiniCPM5-1B" if size == "1B" else "openbmb/MiniCPM5-2B"
        try:
            self.tok = AutoTokenizer.from_pretrained(repo)
        except Exception as exc:
            raise requiresresource(
                f"failed to load tokenizer for {repo}",
                hint="check network or HF cache",
            ) from exc
        try:
            dtypeobj = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[dtype]
            self.model = AutoModelForCausalLM.from_pretrained(repo, torch_dtype=dtypeobj)
        except Exception as exc:
            raise requiresresource(
                f"failed to load weights for {repo}",
                hint="check network, HF_TOKEN, or disk space",
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
        """Encode tokens; return last-hidden-state + pooled vector.

        Args:
            inputids: ``[batch, seqlen]`` token ids.
            attentionmask: ``[batch, seqlen]`` mask (0/1).

        Returns:
            Dict ``{"hiddens": [batch, seqlen, dim], "pooled": [batch, dim]}``.
        """
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
        """Tokenize ``text`` via the bundled tokenizer."""
        return self.tok(text, return_tensors="pt")

    @property
    def hiddendim(self) -> int:
        return int(self.model.config.hidden_size)

    def teachexamples(self) -> list[str]:
        """Few-shot examples suited to MiniCPM5."""
        return ["Q: 2+2?\nA: 4", "Q: capital of France?\nA: Paris"]

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.backbone.minicpm5.latency", "type": "histogram"}]}

    def metrics(self) -> list[Any]:
        return []
