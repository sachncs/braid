"""Plain stdlib log backend."""

from __future__ import annotations

import logging
import os
from typing import Any

from braid.core.registry import registry


@registry.register(category="log", name="plain")
class plain:
    """Plain stdlib logging."""

    name: str = "plain"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def __init__(self, level: str | None = None) -> None:
        level = (level or os.environ.get("BRAID_LOG_LEVEL") or "INFO").upper()
        logging.basicConfig(
            level=getattr(logging, level),
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        self.log = logging.getLogger("braid")

    def info(self, msg: str, **kwargs: Any) -> None:
        self.log.info(msg, extra=kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self.log.warning(msg, extra=kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self.log.error(msg, extra=kwargs)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
