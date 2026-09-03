"""Structlog bootstrap for the braid runtime."""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

import structlog


def configure(
    level: str | None = None,
    formatname: str | None = None,
    *,
    cache: bool = True,
) -> None:
    """Configure structlog.

    Idempotent: safe to call multiple times. Honors ``BRAID_LOG_LEVEL`` and
    ``BRAID_LOG_FORMAT`` env vars when explicit args are not supplied.

    Args:
        level: debug, info, warn, error.
        formatname: ``"json"`` or ``"console"``.
        cache: if True, skip reconfiguration when already configured.
    """
    if cache and getattr(configure, "_configured", False):
        return
    level = (level or os.environ.get("BRAID_LOG_LEVEL") or "INFO").upper()
    formatname = (formatname or os.environ.get("BRAID_LOG_FORMAT") or "json").lower()
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    shared: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
    ]
    if formatname == "json":
        renderer = structlog.processors.JSONRenderer()
    elif formatname == "console":
        renderer = structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty())
    elif formatname == "logfmt":
        renderer = structlog.processors.LogfmtRenderer()
    else:
        renderer = structlog.processors.JSONRenderer()
    shared.append(renderer)
    structlog.configure(
        processors=shared,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level)),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )
    configure._configured = True  # type: ignore[attr-defined]


def getlogger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a configured logger.

    Args:
        name: logger name.

    Returns:
        A structlog bound logger.
    """
    configure()
    return structlog.get_logger(name) if name else structlog.get_logger()
