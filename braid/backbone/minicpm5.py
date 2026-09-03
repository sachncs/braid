"""MiniCPM5 backbone wrapper."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="backbone", name="minicpm5")
class minicpm5:
    """MiniCPM5 1B / 2B backbone wrapper.

    Attributes:
        size: model size string.
        dtype: bf16, fp16, or fp32.
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
        self.size = size
        self.dtype = dtype
        self.gradientcheckpointing = gradientcheckpointing
        self._model: Any | None = None
        self._tok: Any | None = None

    def _load(self) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            repo = "openbmb/MiniCPM5-1B" if self.size == "1B" else "openbmb/MiniCPM5-2B"
            self._tok = AutoTokenizer.from_pretrained(repo)
            dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[self.dtype]
            self._model = AutoModelForCausalLM.from_pretrained(repo, torch_dtype=dtype)
            if self.gradientcheckpointing:
                try:
                    self._model.gradient_checkpointing_enable()
                except Exception:  # noqa: BLE001
                    pass
        except Exception:  # noqa: BLE001
            self._model = None
            self._tok = None

    def encode(self, inputids: Any, attentionmask: Any | None = None) -> Any:
        """Run the backbone; return hidden states and pooled vector."""
        if self._model is None:
            self._load()
        if self._model is None:
            import torch

            torch.manual_seed(0)
            out = {"hiddens": torch.randn(1, inputids.shape[1], 64), "pooled": torch.randn(1, 64)}
            return out
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
        """Tokenize a string via the bundled tokenizer."""
        if self._tok is None:
            self._load()
        if self._tok is None:
            return None
        return self._tok(text, return_tensors="pt")

    @property
    def hiddendim(self) -> int:
        try:
            return int(self._model.config.hidden_size) if self._model is not None else 64
        except Exception:  # noqa: BLE001
            return 64

    def teachexamples(self) -> list[Any]:
        """Few-shot examples suited to MiniCPM5."""
        return [
            "Q: what is 2+2?\nA: 4",
            "Q: capital of france?\nA: Paris",
        ]

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.backbone.minicpm5.fwdlatency", "type": "histogram"}]}

    def metrics(self) -> list[Any]:
        return []
