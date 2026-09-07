"""structlog-JSON log backend."""

from __future__ import annotations

import logging
import os
from typing import Any

import structlog

from braid.core.registry import registry


@registry.register(category="log", name="structlogjson")
class structlogjson:
    """structlog backed by JSON renderer."""

    name: str = "structlogjson"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def __init__(self, level: str | None = None) -> None:
        level = (level or os.environ.get("BRAID_LOG_LEVEL") or "INFO").upper()
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
        """Log an info-level message."""
        self.log.info(msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        """Log a warning-level message."""
        self.log.warning(msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        """Log an error-level message."""
        self.log.error(msg, **kwargs)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
