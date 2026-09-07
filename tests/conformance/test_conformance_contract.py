"""Sweep all concretes through the polymorphic conformance harness."""

import pytest

import braid
from braid.core.conformance import verifyone


def _allconcretes():
    """Yield (category, name) pairs across the registry."""
    for c in braid.registry.categories():
        for n in braid.registry.available(c):
            yield c, n


@pytest.mark.parametrize("category,name", list(_allconcretes()))
def test_conformance(category: str, name: str) -> None:
    """Every concrete passes its declared contracts (or is skipped if it can't construct)."""
    result = verifyone(category, name)
    assert result.passed, f"{category}.{name} failed: {result.failures}"
