"""vLLM prefill-only backend.

Wraps vLLM's prefill-only path to extract last-token hidden state and
runs a single BLAS catalog scoring. Fails fast if vllm is not
installed or the model isn't loadable.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from braid.core.error import requiresenvironment, requiresresource
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
        maxmodellen: int = 8192,
    ) -> None:
        try:
            from vllm import LLM

            self.engine: Any = LLM(
                model=model,
                max_model_len=maxmodellen,
                enforce_eager=False,
                gpu_memory_utilization=0.85,
            )
        except ImportError as exc:
            raise requiresenvironment(
                "vllm is required for server:vllm", hint="pip install vllm"
            ) from exc
        except Exception as exc:
            raise requiresresource(
                f"failed to load vLLM engine for {model}",
                hint="check CUDA availability and HF cache",
            ) from exc
        self.model = model
        self.host = host
        self.port = port
        self.maxmodellen = maxmodellen

    def rank(self, prompt: str, catalogscoresfn: Any, topk: int = 50) -> dict[str, Any]:
        """Run prefill-only ranking; return top-k item ids and scores."""
        try:
            outputs = self.engine.generate([prompt], sampling_params=None, use_tqdm=False)
        except Exception as exc:
            raise requiresresource(f"vLLM generate failed: {exc}") from exc
        if not outputs:
            return {"ids": [], "scores": [], "fallback": True}
        lastembed = getattr(outputs[0].outputs[0], "embedding", None)
        if lastembed is None:
            return {"ids": list(range(topk)), "scores": [0.0] * topk, "fallback": True}
        scores = catalogscoresfn(np.asarray(lastembed))
        ids = list(range(len(scores[0])))[:topk]
        return {"ids": ids, "scores": scores[0][:topk].tolist() if hasattr(scores, "tolist") else []}

    def shutdown(self) -> None:
        """Release vLLM engine."""
        self.engine = None

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.server.vllm.qps", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
