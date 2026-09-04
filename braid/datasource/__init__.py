"""Data sources registered with the registry.

Module exposes 1 concrete: ``localparquet``.
"""

from braid.datasource.localparquet import localparquet

__all__ = ["localparquet"]
