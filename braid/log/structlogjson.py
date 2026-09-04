"""structlog-JSON log backend."""

from __future__ import annotations

import logging
from typing import Any

import structlog

from braid.core.registry import registry


@registry.register(category="log", name="structlogjson")
class structlogjson:
    """structlog-JSON log backend."""

    name: str = "structlogjson"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def __init__(self, level: str = "INFO") -> None:
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level)),
            logger_factory=structlog.PrintLoggerFactory(),
        )
        self.log = structlog.get_logger("braid")

    def info(self, msg: str, **kwargs: Any) -> None:
        self.log.info(msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self.log.warning(msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self.log.error(msg, **kwargs)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
