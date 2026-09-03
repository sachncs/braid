"""Triton Inference Server backend."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="server", name="triton")
class triton:
    """Triton Inference Server backend."""

    name: str = "triton"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"prefixcache", "gpu", "lowlatency", "async", "observable"})

    def __init__(self, url: str = "localhost:8001", modelname: str = "braid") -> None:
        self.url = url
        self.modelname = modelname
        self._client: Any | None = None

    def warmup(self) -> None:
        try:
            import tritonclient.http as tritonhttp

            self._client = tritonhttp.InferenceServerClient(url=self.url)
        except Exception:  # noqa: BLE001
            self._client = None

    def rank(self, prompt: str, catalogscoresfn: Any, topk: int = 50) -> dict[str, Any]:
        if self._client is None:
            self.warmup()
        if self._client is None:
            return {"ids": [], "scores": [], "fallback": True}
        try:
            import tritonclient.http as tritonhttp

            inp = tritonhttp.InferInput("INPUT", [1, len(prompt)], "INT64")
            inp.set_data_from_numpy(__import__("numpy").array([[ord(c) for c in prompt]], dtype="int64"))
            result = self._client.infer(model_name=self.modelname, inputs=[inp])
            out = result.as_numpy("OUTPUT")
            ids = list(range(int(out.shape[-1])))[:topk]
            scores = out.flatten()[:topk].tolist()
            return {"ids": ids, "scores": scores}
        except Exception:  # noqa: BLE001
            return {"ids": [], "scores": [], "fallback": True}

    def shutdown(self) -> None:
        self._client = None

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.server.triton.qps", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
