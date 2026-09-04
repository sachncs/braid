"""Distillation training phase.

Distills a teacher model into a smaller student. Real implementation arrives in O5.
"""

from __future__ import annotations

from typing import Any

from braid.core.logging import getlogger
from braid.core.registry import registry


@registry.register(category="phase", name="distill")
class distill:
    """Distillation training phase.

    Attributes:
        teacher: teacher registry name.
        student: student registry name.
        temperature: KD temperature.
    """

    name: str = "distill"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"async", "observable"})

    def __init__(self, teacher: str = "minicpm5", student: str = "pythia1", temperature: float = 2.0) -> None:
        """Initialize the distillation phase.

        Args:
            teacher: registry name of the teacher backbone. Defaults to ``"minicpm5"``.
            student: registry name of the student backbone. Defaults to ``"pythia1"``.
            temperature: KD temperature. Defaults to 2.0.
        """
        self.teacher = teacher
        self.student = student
        self.temperature = temperature

    def setup(self) -> None:
        return None

    def run(self) -> dict[str, Any]:
        log = getlogger("braid.phase.distill")
        log.info("distill.start", teacher=self.teacher, student=self.student)
        return {"phase": "distill", "teacher": self.teacher, "student": self.student}

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
