"""Shared type aliases and ``TypeVar``s used across braid."""

from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
K = TypeVar("K")

I = TypeVar("I", contravariant=True)  # noqa: E741 — Input typevar
O = TypeVar("O", covariant=True)  # noqa: E741 — Output typevar
