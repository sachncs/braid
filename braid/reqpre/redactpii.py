"""PII redaction preprocessor."""

from __future__ import annotations

import re
from typing import Any

from braid.core.registry import registry


EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")


@registry.register(category="reqpre", name="redactpii")
class redactpii:
    """Redact emails and phone numbers from string fields."""

    name: str = "redactpii"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", })

    def redact(self, value: str) -> str:
        return EMAIL.sub("[email]", PHONE.sub("[phone]", value))

    def process(self, request: dict[str, Any]) -> dict[str, Any]:
        """Strip PII from string fields."""
        out: dict[str, Any] = {}
        for k, v in request.items():
            if isinstance(v, str):
                out[k] = self.redact(v)
            elif isinstance(v, dict):
                out[k] = self.process(v)
            elif isinstance(v, list):
                out[k] = [self.process(x) if isinstance(x, dict) else (self.redact(x) if isinstance(x, str) else x) for x in v]
            else:
                out[k] = v
        return out

    def observability(self) -> dict[str, Any]:
        return {"metrics": [{"name": "braid.reqpre.redactions", "type": "counter"}]}

    def metrics(self) -> list[Any]:
        return []
