"""Sweep all concretes through the polymorphic conformance harness."""

import pytest

import braid
from braid.core.conformance import verifyone


pytestmark = pytest.mark.conformance


def _allconcretes():
    """Yield (category, name) pairs across the registry."""
    for c in braid.registry.categories():
        for n in braid.registry.available(c):
            yield c, n


@pytest.mark.parametrize("category,name", list(_allconcretes()))
def test_conformance(category: str, name: str) -> None:
    """Every concrete either passes its declared contracts or is skipped."""
    result = verifyone(category, name)
    assert result.passed or result.skipped, (
        f"{category}.{name} failed: {result.failures}"
    )
