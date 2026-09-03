"""Polymorphic data source Protocol."""

from __future__ import annotations

from typing import Any, Iterator, Protocol, runtime_checkable


@runtime_checkable
class datasource(Protocol):
    """A category protocol.

    All concretes in this module implement ``read``, optionally ``aread``,
    plus declared lifecycle/observability hooks.
    """

    name: str

    def read(self) -> Iterator[dict[str, Any]]: ...
