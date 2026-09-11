"""Reward tests."""

import pytest

pytestmark = pytest.mark.integration


def test_compositereward_runs() -> None:
    """Composite reward returns a scalar in [0, 1]."""
    import braid

    composite = braid.rewards.compositereward([("diversitybonus", 0.5)])
    val = composite.score({"itemid": 1, "duration": 60.0}, {"recent": [{"itemid": 2}, {"itemid": 3}]})
    assert 0 <= val <= 1


def test_diversity_bonus() -> None:
    """Diversity bonus increases for rare items."""
    import braid

    r = braid.rewards.diversitybonus(recentk=10)
    history = [{"itemid": 1} for _ in range(10)]
    rare = r.score({"itemid": 99}, history=history)
    common = r.score({"itemid": 1}, history=history)
    assert rare > common
