"""Data sources registered with the registry.

Module exposes 1 concrete: ``localparquet``. ``s3parquet``, ``kafka``, ``postgres``
were removed (network/external-service dependencies).
"""

from braid.datasource.localparquet import localparquet

__all__ = ["localparquet"]
