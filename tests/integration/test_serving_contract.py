"""Serving tests."""


def test_lru_cache() -> None:
    """LRU cache puts and gets."""
    import braid

    c = braid.registry.create("cache", "lru", maxentries=10)
    c.put("a", 1)
    assert c.get("a") == 1
    assert c.get("missing") is None


def test_tokenbucket_allows_burst() -> None:
    """Token bucket allows the first burst, then denies."""
    import braid

    b = braid.registry.create("ratelimit", "tokenbucket", rate=1.0, capacity=2.0)
    assert b.allow("k")
    assert b.allow("k")
    assert not b.allow("k")


def test_reqpre_normalize_lowercases() -> None:
    """Normalize lowercases string fields."""
    import braid

    rp = braid.registry.create("reqpre", "normalize")
    out = rp.process({"X": "FOO", "Y": "BAR"})
    assert out["X"] == "foo"
    assert out["Y"] == "bar"


def test_resppost_calibrate_scales() -> None:
    """Calibrate scales scores by 1/temperature."""
    import braid

    pp = braid.registry.create("resppost", "calibrate", temperature=2.0)
    out = pp.process({"ids": [1, 2], "scores": [4.0, 2.0]})
    assert out["scores"] == [2.0, 1.0]
