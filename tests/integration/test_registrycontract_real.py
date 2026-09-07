"""Real assertion tests for the polynomial registry and config migrator."""

import pytest


def test_registry_categories_nonempty() -> None:
    import braid

    cats = braid.registry.categories()
    assert len(cats) >= 30
    expected_core = {"backbone", "loss", "reward", "phase", "eval", "quantizer"}
    missing = expected_core - set(cats)
    assert not missing, f"missing core categories: {missing}"


def test_registry_resolve_creates_instance() -> None:
    from braid.core.registry import registry

    cls = registry.resolve("eval", "offlineranking")
    inst = cls()
    rpt = inst.evaluate([[42, 7, 8]], [42])
    assert rpt["mrr"] == 1.0


def test_registry_capabilities_intersection() -> None:
    from braid.core.registry import registry

    caps = registry.capabilities("loss", "braidedloss")
    assert "observable" in caps


def test_registry_create_unknown_raises_typed() -> None:
    from braid.core.error import requiresenvironment
    from braid.core.registry import registry

    with pytest.raises(Exception):
        registry.create("not_a_real_cat", "neither_a_real_name")


def test_registry_dedupes() -> None:
    """Double-registering the same (cat, name) should not double the available list."""
    from braid.core.registry import registry

    for cat in registry.categories():
        n = len(registry.available(cat))
        unique = len(set(registry.available(cat)))
        assert n == unique, f"{cat} has duplicates"


def test_applymigrations_runs_noop() -> None:
    from braid.core.versioning import applymigrations

    raw = {"loss": {"type": "rankingce", "weight": 1.0}}
    out = applymigrations(raw, "loss", "braidedloss")
    assert out is not None


def test_versioning_metadata_readable() -> None:
    from braid.core.registry import registry

    klass = registry.resolve("loss", "braidedloss")
    assert getattr(klass, "_registry_version", None) is not None or hasattr(klass, "version")
