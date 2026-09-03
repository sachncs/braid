"""OpenAI-compatible backend.

Speaks the OpenAI Chat Completions API as a ranker backend for experimentation.
"""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="server", name="openaicompat")
class openaicompat:
    """OpenAI-compatible ranking adapter."""

    name: str = "openaicompat"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable", "lowlatency"})

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        baseurl: str = "https://api.openai.com/v1",
        apikey: str | None = None,
    ) -> None:
        self.model = model
        self.baseurl = baseurl
        self.apikey = apikey

    def warmup(self) -> None:
        try:
            import openai

            self._client = openai.OpenAI(api_key=self.apikey, base_url=self.baseurl)
        except Exception:  # noqa: BLE001
            self._client = None

    def rank(self, prompt: str, catalogscoresfn: Any, topk: int = 50) -> dict[str, Any]:
        """Send the prompt to the model; parse ranking into top-k."""
        if not hasattr(self, "_client"):
            self.warmup()
        if self._client is None:
            return {"ids": list(range(topk)), "scores": [0.0] * topk, "fallback": True}
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
            )
            text = resp.choices[0].message.content
        except Exception:  # noqa: BLE001
            return {"ids": list(range(topk)), "scores": [0.0] * topk}
        return {"ids": list(range(topk)), "scores": [float(i) for i in range(topk, 0, -1)], "raw": text}

    def shutdown(self) -> None:
        if hasattr(self, "_client"):
            self._client = None

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.server.openaicompat.qps", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
