"""Datamodule glue: pin a datasource + sessionizer + splitter together."""

from __future__ import annotations

from typing import Any

from braid.core.registry import registry
from braid.splitter.chronological import chronologicalsplitter
from braid.splitter.leaveoneout import leaveoneoutsplitter
from braid.splitter.timestratified import timestratifiedsplitter


class datamodule:
    """Glues a datasource + splitter.

    Attributes:
        datasource: a datasource concrete.
        splitter: a splitter concrete.
    """

    def __init__(self, datasource: Any, splitter: Any | None = None) -> None:
        self.datasource = datasource
        self.splitter = splitter or chronologicalsplitter()

    def splits(self) -> tuple[list, list, list]:
        """Compute train/val/test."""
        rows = list(self.datasource.read())
        return self.splitter.split(rows)

    def tobatchstrategy(self, name: str = "packed", **kwargs: Any) -> Any:
        from braid.batcher.packedbatcher import packedbatcher
        from braid.batcher.paddedbatcher import paddedbatcher

        if name == "packed":
            return packedbatcher(**kwargs)
        return paddedbatcher(**kwargs)
