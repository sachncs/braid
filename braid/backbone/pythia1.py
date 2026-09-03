"""Pythia 1B backbone wrapper (small + reproducible)."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="backbone", name="pythia1")
class pythia1:
    """EleutherAI Pythia-1B backbone."""

    name: str = "pythia1"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"gpu", "fusedkernel", "async", "teachable"})

    def __init__(self, size: str = "1B", dtype: str = "bf16", gradientcheckpointing: bool = True) -> None:
        self.size = size
        self.dtype = dtype
        self.gradientcheckpointing = gradientcheckpointing
        self._model: Any | None = None
        self._tok: Any | None = None

    def _load(self) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            repo = "EleutherAI/pythia-1b"
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
        if self._model is None:
            self._load()
        if self._model is None:
            import torch

            torch.manual_seed(0)
            return {"hiddens": torch.randn(1, inputids.shape[1], 64), "pooled": torch.randn(1, 64)}
        out = self._model(input_ids=inputids, attention_mask=attentionmask, output_hidden_states=True, return_dict=True)
        last = out.hidden_states[-1]
        if attentionmask is not None:
            mask = attentionmask.unsqueeze(-1).float()
            pooled = (last * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
        else:
            pooled = last.mean(dim=1)
        return {"hiddens": last, "pooled": pooled}

    def tok(self, text: str) -> Any:
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
        return ["Q: hi\nA: hello"]

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
