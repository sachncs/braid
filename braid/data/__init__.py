"""Data subsystem.

Data: local parquet source, sink, sessionizer, splitter, metadata, ingest, schemas.
"""

from braid.datasource import localparquet
from braid.datasink import parquetsink, arrowsink
from braid.sessionizer import gapsessionizer, countsessionizer, timewindowsessionizer
from braid.splitter import chronologicalsplitter, leaveoneoutsplitter, timestratifiedsplitter
from braid.metadata import csvmetadata, jsonapi, embedded

try:
    from braid.data.schemas import validateevents, validateitems  # noqa: F401
except ImportError:

    def validateevents(df):
        return None

    def validateitems(df):
        return None


__all__ = [
    "localparquet",
    "parquetsink",
    "arrowsink",
    "gapsessionizer",
    "countsessionizer",
    "timewindowsessionizer",
    "chronologicalsplitter",
    "leaveoneoutsplitter",
    "timestratifiedsplitter",
    "csvmetadata",
    "jsonapi",
    "embedded",
    "validateevents",
    "validateitems",
]
