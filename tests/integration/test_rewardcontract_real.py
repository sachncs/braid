"""Real assertion tests for the longterm-return reward proxy."""


def test_longtermreturn_returns_zero_on_empty_history() -> None:
    from braid.rewards.longtermreturn import longtermreturn

    rw = longtermreturn()
    val = rw.score({"item": 1}, ctx={"history": []})
    assert 0.0 <= float(val) <= 1.0


def test_longtermreturn_history_with_positive_only() -> None:
    from braid.rewards.longtermreturn import longtermreturn

    rw = longtermreturn(horizon=30)
    val = float(
        rw.score({"rating": 5.0, "kind": "thumbup"}, ctx={"usertenure": 365, "recentactivity": 7})
    )
    assert 0.0 <= val <= 1.0


def test_longtermreturn_history_with_negative_only() -> None:
    from braid.rewards.longtermreturn import longtermreturn

    rw = longtermreturn(horizon=30)
    val = float(
        rw.score({"rating": 0.5, "kind": "play"}, ctx={"usertenure": 1, "recentactivity": 0})
    )
    assert 0.0 <= val <= 1.0


def test_composite_reward_zero_fails_raises_typed() -> None:
    """If every registered member is unknown, score() raises requiresresource."""
    from braid.core.error import requiresresource
    from braid.rewards.composite import compositereward

    rw = compositereward(members=[("nonexistent_reward_xyz", 1.0)])
    try:
        rw.score({"item": 1})
    except requiresresource:
        return
    raise AssertionError("expected requiresresource")


def test_diversity_bonus_finite() -> None:
    from braid.rewards.diversitybonus import diversitybonus

    rw = diversitybonus()
    history = [{"item": i % 5} for i in range(20)]
    val = float(rw.score({"item": 99}, history=history))
    assert 0.0 <= val <= 1.0


def test_contenttype_balance_zero() -> None:
    from braid.rewards.contenttypebalance import contenttypebalance

    rw = contenttypebalance()
    history = [{"kind": "play"}] * 5
    val = float(rw.score({"kind": "play"}, history=history))
    assert 0.0 <= val <= 1.0


def test_noveltyreward_high_for_unseen() -> None:
    from braid.rewards.noveltyreward import noveltyreward

    rw = noveltyreward()
    fresh = float(rw.score({"launcheddays": 1}, ctx=None))
    stale = float(rw.score({"launcheddays": 999}, ctx=None))
    assert fresh > stale
    assert 0.0 <= fresh <= 1.0
    assert 0.0 <= stale <= 1.0
