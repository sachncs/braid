"""Plain log backend."""

from __future__ import annotations

import logging
from typing import Any

from braid.core.registry import registry


@registry.register(category="log", name="plain")
class plain:
    """Plain log backend (basic stdlib)."""

    name: str = "plain"
    version: str = "1.0.0"
    capabilities: frozenset[str] = frozenset({"observable", "lowlatency"})

    def __init__(self, level: str = "INFO") -> None:
        logging.basicConfig(level=getattr(logging, level), format="%(asctime)s %(levelname)s %(name)s %(message)s")
        self._log = logging.getLogger("braid")

    def info(self, msg: str, **kwargs: Any) -> None:
        self._log.info(msg, extra=kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._log.warning(msg, extra=kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self._log.error(msg, extra=kwargs)

    def observability(self) -> dict[str, Any]:
        return {}

    def metrics(self) -> list[Any]:
        return []
