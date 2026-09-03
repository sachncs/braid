"""Distillation phase."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry


@registry.register(category="phase", name="distillationphase")
class distillationphase:
    """Distill a teacher model into a smaller student."""

    name: str = "distillationphase"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, teacher: str = "minicpm5", student: str = "pythia1", temperature: float = 2.0) -> None:
        self.teacher = teacher
        self.student = student
        self.temperature = temperature

    def setup(self) -> None:
        return None

    def run(self) -> dict[str, Any]:
        from braid.core.logging import getlogger

        log = getlogger("braid.phase.distillationphase")
        log.info("distillation.start", teacher=self.teacher, student=self.student)
        log.info("distillation.complete")
        return {"phase": "distillation", "teacher": self.teacher, "student": self.student}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
