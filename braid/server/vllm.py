"""vLLM-based serving backend.

Wraps vLLM with prefill-only hidden-state extraction and a catalog-scoring
matmul. The PolyMorphic runtime: same protocol as ``hflocal`` and ``triton``.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="server", name="vllm")
class vllm:
    """vLLM prefill-only ranker backend."""

    name: str = "vllm"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"prefixcache", "gpu", "speculative", "lowlatency", "async", "observable"})

    def __init__(
        self,
        model: str = "openbmb/MiniCPM5-1B",
        host: str = "0.0.0.0",
        port: int = 8080,
        maxmodel_len: int = 8192,
    ) -> None:
        self.model = model
        self.host = host
        self.port = port
        self.maxmodel_len = maxmodel_len
        self.engine: Any | None = None

    def warmup(self) -> None:
        """Load the vLLM engine."""
        try:
            from vllm import LLM

            self.engine = LLM(
                model=self.model,
                max_model_len=self.maxmodel_len,
                enforce_eager=False,
                gpu_memory_utilization=0.85,
            )
        except Exception:  # noqa: BLE001 — degraded mode
            self.engine = None

    def rank(self, prompt: str, catalogscoresfn: Any, topk: int = 50) -> dict[str, Any]:
        """Run prefill-only ranking; return top-k item ids and scores."""
        if self.engine is None:
            self.warmup()
        if self.engine is None:
            return {"ids": [], "scores": [], "fallback": True}
        try:
            outputs = self.engine.generate([prompt], sampling_params=None, use_tqdm=False, prompt_logprobs=0)
        except Exception:  # noqa: BLE001
            return {"ids": [], "scores": [], "fallback": True}
        lastembed = outputs[0].outputs[0].embedding if hasattr(outputs[0].outputs[0], "embedding") else None
        scores = catalogscoresfn(lastembed)
        ids = list(range(len(scores[0])))[:topk]
        return {"ids": ids, "scores": scores[0][:topk].tolist() if hasattr(scores, "tolist") else []}

    def shutdown(self) -> None:
        self.engine = None

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.server.vllm.qps", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
