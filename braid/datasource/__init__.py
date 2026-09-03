"""Data sources registered with the registry.

Module exposes 4 concretes: ``localparquet``, ``s3parquet``, ``kafka``, ``postgres``.
All satisfy ``streamable``, ``asyncable``, ``persistable``, ``observable`` traits.
"""

from braid.datasource.localparquet import localparquet
from braid.datasource.s3parquet import s3parquet
from braid.datasource.kafka import kafka
from braid.datasource.postgres import postgres

__all__ = ["localparquet", "s3parquet", "kafka", "postgres"]
