"""Data sinks."""

from braid.datasink.parquetsink import parquetsink
from braid.datasink.arrowsink import arrowsink
from braid.datasink.postgres import postgres

__all__ = ["parquetsink", "arrowsink", "postgres"]
