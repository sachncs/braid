"""Calibrate response scores via temperature scaling."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="resppost", name="calibrate")
class calibrate:
    """Temperature-scale response scores."""

    name: str = "calibrate"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "idempotent", "lowlatency"})

    def __init__(self, temperature: float = 1.0) -> None:
        if temperature <= 0:
            raise ValueError("temperature must be > 0")
        self.temperature = temperature

    def process(self, response: dict[str, Any]) -> dict[str, Any]:
        scores = response.get("scores", [])
        if not scores:
            return response
        scaled = [s / self.temperature for s in scores]
        return {**response, "scores": scaled, "calibrated": True}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
