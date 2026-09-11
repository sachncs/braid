"""Pandera schemas for braid value objects (optional).

If pandera is not installed, the schema helpers degrade gracefully.
"""

from __future__ import annotations

try:
    import pandera as pa  # noqa: F401
    from pandera import Check, Column, DataFrameSchema, Index

    EVENT_SCHEMA = DataFrameSchema(
        columns={
            "userid": Column(int, Check.greater_than_or_equal_to(0)),
            "itemid": Column(int, Check.greater_than_or_equal_to(0)),
            "kind": Column(str, Check.isin(["play", "thumbup", "thumbdown", "add", "click"])),
            "rating": Column(float, Check.in_range(0.0, 5.0), nullable=True),
            "duration": Column(float, Check.greater_than_or_equal_to(0), nullable=True),
            "timestamp": Column(float, Check.greater_than_or_equal_to(0)),
        },
        index=Index(int),
        strict=True,
    )

    ITEM_SCHEMA = DataFrameSchema(
        columns={
            "itemid": Column(int, unique=True),
            "title": Column(str),
            "genres": Column(str),
            "year": Column(int, Check.in_range(1800, 2100), nullable=True),
        },
        strict=False,
    )
except ImportError:
    EVENT_SCHEMA = None
    ITEM_SCHEMA = None


def validateevents(df) -> None:
    """Validate an events dataframe (no-op if pandera missing)."""
    if EVENT_SCHEMA is None:
        return
    EVENT_SCHEMA.validate(df)


def validateitems(df) -> None:
    """Validate an items dataframe (no-op if pandera missing)."""
    if ITEM_SCHEMA is None:
        return
    ITEM_SCHEMA.validate(df)
