"""Observability declarations.

Every concrete that emits metrics, traces, or logs declares them via the
``metricdecl``, ``tracedecl``, and ``logdecl`` types. The ``obsgen`` CLI
generates Prometheus alert rules and Grafana panels from these declarations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class metricdecl:
    """Declaration of a single metric.

    Attributes:
        name: dotted metric name, e.g., ``braid.catalogstore.score.duration``.
        type: counter, gauge, histogram, or summary.
        labels: label keys expected on every emission.
        description: free-form description.
    """

    name: str
    type: Literal["counter", "gauge", "histogram", "summary"]
    labels: tuple[str, ...] = ()
    description: str = ""


@dataclass(frozen=True)
class tracedecl:
    """Declaration of a single trace span.

    Attributes:
        name: span name.
        attributes: attribute keys set on the span.
        events: span events emitted.
    """

    name: str
    attributes: tuple[str, ...] = ()
    events: tuple[str, ...] = ()


@dataclass(frozen=True)
class logdecl:
    """Declaration of a single log channel.

    Attributes:
        name: logger name.
        level: default level.
        fields: structured fields commonly emitted.
    """

    name: str
    level: Literal["debug", "info", "warn", "error"]
    fields: tuple[str, ...] = ()


@dataclass
class observabilityspec:
    """Bundle of observability declarations for a single concrete."""

    metrics: list[metricdecl] = field(default_factory=list)
    traces: list[tracedecl] = field(default_factory=list)
    logs: list[logdecl] = field(default_factory=list)


def normalize(metricname: str) -> str:
    """Normalize a metric name into the braid dotted convention.

    Example:
        >>> normalize("score duration")
        'score.duration'
    """
    return metricname.strip().replace(" ", ".").replace("/", ".").lower()
