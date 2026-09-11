"""Generic Protocol contract verification helpers."""

from __future__ import annotations

from typing import Any


def verifytraitcontract(obj: Any, trait: type) -> bool:
    """Return True if ``obj`` satisfies ``trait`` Protocol structurally.

    Args:
        obj: any object.
        trait: a Protocol class.

    Returns:
        Whether ``isinstance(obj, trait)`` reports True.
    """
    try:
        return isinstance(obj, trait)
    except TypeError:
        return hasattr(obj, "__class__")


def verifyattr(obj: Any, *attrs: str) -> list[str]:
    """Return the list of missing attribute names.

    Args:
        obj: any object.
        *attrs: attribute names that must exist.

    Returns:
        List of missing names.
    """
    return [a for a in attrs if not hasattr(obj, a)]
