"""Shared type aliases and ``TypeVar``s used across braid."""
from __future__ import annotations

from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
K = TypeVar("K")

I = TypeVar("I", contravariant=True)
O = TypeVar("O", covariant=True)
