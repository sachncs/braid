"""Verify the registry exposes every concrete in every category."""

import pytest

import braid


def test_registry_categories_populated() -> None:
    """Verify every category has at least one registered concrete."""
    cats = braid.registry.categories()
    assert len(cats) >= 40, f"expected >= 40 categories, got {len(cats)}"


def test_registry_total_concretes() -> None:
    """Verify total concretes >= 140."""
    total = sum(len(braid.registry.available(c)) for c in braid.registry.categories())
    assert total >= 140, f"expected >= 140 concretes, got {total}"


def test_categories_are_sorted_lists() -> None:
    """available() returns sorted lists."""
    for c in braid.registry.categories():
        items = braid.registry.available(c)
        assert items == sorted(items)


def test_registry_create_round_trip() -> None:
    """create() returns an instance and resolve() returns a class."""
    store = braid.registry.create("catalogstore", "matmulinmem", embeddings=[[1.0, 2.0], [3.0, 4.0]])
    assert hasattr(store, "score")
    klass = braid.registry.resolve("catalogstore", "matmulinmem")
    assert klass.__name__ == "matmulinmem"


def test_registry_unknown_raises() -> None:
    """Unknown registry name raises registryerror."""
    from braid.core.error import registryerror

    with pytest.raises(registryerror):
        braid.registry.create("catalogstore", "nonexistent")
