"""Composable mixin Protocols (a.k.a. traits).

Category Protocols compose traits they require. Concrete classes are checked
against the trait contracts by the conformance harness.
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Iterator, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


@runtime_checkable
class streamable(Protocol):
    """Trait: produces a stream of values."""

    def openstream(self) -> Iterator[T]: ...


@runtime_checkable
class asyncable(Protocol):
    """Trait: provides async variants of its public methods."""

    def arun(self, *args: Any, **kwargs: Any) -> Any: ...


@runtime_checkable
class cachable(Protocol):
    """Trait: has an in-memory cache layer."""

    def cacheget(self, key: K) -> V | None: ...
    def cacheput(self, key: K, value: V) -> None: ...
    def cacheinvalidate(self, key: K) -> None: ...


@runtime_checkable
class persistable(Protocol):
    """Trait: persists state across restarts."""

    def persist(self, path: str) -> None: ...
    def restore(self, path: str) -> None: ...


@runtime_checkable
class observable(Protocol):
    """Trait: emits metrics, traces, and logs.

    Classes implementing this trait declare observability via the
    ``observability`` Protocol and emit events through the runtime sink.
    """

    def observability(self) -> Any: ...


@runtime_checkable
class idempotent(Protocol):
    """Trait: produces identical output for the same idempotency key."""

    def idempotencykey(self, *args: Any, **kwargs: Any) -> str: ...


@runtime_checkable
class distributable(Protocol):
    """Trait: supports distributed execution."""

    def shardrank(self) -> int: ...
    def numshards(self) -> int: ...


@runtime_checkable
class teachable(Protocol):
    """Trait: accepts in-context examples or few-shots."""

    def teachexamples(self) -> list[Any]: ...


@runtime_checkable
class circuitbreaker(Protocol):
    """Trait: trips on repeated failure, half-opens after cooldown."""

    def trip(self) -> None: ...
    def reset(self) -> None: ...
    def isopen(self) -> bool: ...


ALL_TRAITS: tuple[type, ...] = (
    streamable,
    asyncable,
    cachable,
    persistable,
    observable,
    idempotent,
    distributable,
    teachable,
    circuitbreaker,
)
