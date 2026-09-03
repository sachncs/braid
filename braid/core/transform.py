"""Composable typed transforms and a generic pipeline."""

from __future__ import annotations

from typing import Generic, Protocol, runtime_checkable

from braid.core.context import requestcontext
from braid.core.types import I, O


@runtime_checkable
class transform(Protocol, Generic[I, O]):
    """A typed unit of work.

    Implementations declare their input/output types via ``iotype``.
    """

    def transform(self, input: I, ctx: requestcontext) -> O: ...


class pipeline(transform, Generic[I, O]):
    """Composable list of transforms chained together.

    Example:
        >>> pipe = pipeline(validate(), normalize())
        >>> result = pipe.transform(raw, ctx)
    """

    def __init__(self, *steps: transform) -> None:
        self.steps = list(steps)

    def transform(self, input: object, ctx: requestcontext) -> object:
        for step in self.steps:
            input = step.transform(input, ctx)
        return input


class identity(transform):
    """A transform that returns input unchanged.

    Useful as a default in pipelines and tests.
    """

    def transform(self, input: object, ctx: requestcontext) -> object:
        return input
