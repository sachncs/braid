"""Data subsystem."""

from braid.datasource import localparquet, s3parquet, kafka, postgres
from braid.datasink import parquetsink, arrowsink, postgres
from braid.sessionizer import gapsessionizer, countsessionizer, timewindowsessionizer
from braid.splitter import chronologicalsplitter, leaveoneoutsplitter, timestratifiedsplitter
from braid.metadata import csvmetadata, jsonapi, embedded
from braid.data.ingest import ingest
try:
    from braid.data.schemas import validateevents, validateitems  # noqa: F401
except ImportError:
    def validateevents(df):
        return None

    def validateitems(df):
        return None

__all__ = [
    "localparquet",
    "s3parquet",
    "kafka",
    "postgres",
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
    "ingest",
    "validateevents",
    "validateitems",
]
