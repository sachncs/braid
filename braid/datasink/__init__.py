"""Data sinks."""

from braid.datasink.parquetsink import parquetsink
from braid.datasink.arrowsink import arrowsink

__all__ = ["parquetsink", "arrowsink"]
