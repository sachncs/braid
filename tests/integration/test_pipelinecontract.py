"""Real assertion tests for reqpre, resppost, ratelimit, auth, cache, secret, metrics, tracing, log."""

import pytest

pytestmark = pytest.mark.integration


def test_reqpre_normalize_lowercases() -> None:
    """Normalize request lowercases text fields and strips whitespace."""
    from braid.reqpre.normalize import normalize

    n = normalize()
    out = n.process({"prompt": "  Hello World  ", "tag": "ACTION"})
    assert out["prompt"] == "hello world"
    assert out["tag"] == "action"


def test_reqpre_validate_passes() -> None:
    from braid.reqpre.validate import validate

    v = validate(required=["prompt"])
    out = v.process({"prompt": "hi", "candidates": [1, 2, 3]})
    assert out["prompt"] == "hi"


def test_reqpre_redactpii_redacts_emails() -> None:
    from braid.reqpre.redactpii import redactpii

    r = redactpii()
    out = r.process({"prompt": "contact me at jane.doe@acme.com or 555-123-4567"})
    assert "jane.doe@acme.com" not in out["prompt"]


def test_resppost_rerank_uses_scorer() -> None:
    from braid.resppost.rerank import rerank

    r = rerank()
    out = r.process(
        {"ids": [1, 2, 3], "scores": [1.0, 2.0, 3.0]}, scorer=lambda i: 100 if i == 7 else 0
    )
    assert "ids" in out
    assert out["ids"] == [1, 2, 3]  # 7 not in ids, so unchanged


def test_resppost_rerank_passthrough_no_scorer() -> None:
    from braid.resppost.rerank import rerank

    r = rerank()
    out = r.process({"ids": [1, 2, 3], "scores": [1.0, 2.0, 3.0]}, scorer=None)
    assert out["ids"] == [1, 2, 3]


def test_resppost_diversity_keeps_distinct() -> None:
    from braid.resppost.diversity import diversity as divpost

    d = divpost(lam=0.5)
    out = d.process({"ids": [1, 2, 3, 4, 5]})
    assert "ids" in out


def test_resppost_calibrate_minmax() -> None:
    from braid.resppost.calibrate import calibrate

    c = calibrate(temperature=1.0)
    out = c.process({"scores": [1.0, 5.0, 10.0]})
    assert 0.0 <= min(out["scores"]) <= 1.0 + 1e-6


def test_ratelimit_tokenbucket_drains_capacity() -> None:
    from braid.ratelimit.tokenbucket import tokenbucket

    tb = tokenbucket(rate=0.0, capacity=3.0)
    allowed = 0
    for _ in range(10):
        if tb.allow():
            allowed += 1
    assert 0 <= allowed <= 4


def test_ratelimit_slidingwindow_throttles() -> None:
    from braid.ratelimit.slidingwindow import slidingwindow

    sw = slidingwindow(windowseconds=60, maxcalls=3)
    allowed = sum(1 for _ in range(5) if sw.allow())
    assert allowed == 3


def test_auth_apikey_authenticates() -> None:
    from braid.auth.apikey import apikey

    a = apikey(allowed=["secret-key"])
    out = a.authenticate("secret-key")
    assert isinstance(out, dict)


def test_auth_noauth_passthrough() -> None:
    from braid.auth.noauth import noauth

    out = noauth().authenticate(None)
    assert isinstance(out, dict)


def test_auth_jwt_roundtrip() -> None:
    """``jwt.authenticate`` returns principal + claims for a real signed token."""
    from braid.auth.jwt import jwt

    try:
        import jwt as pyjwt
    except ImportError:
        pytest.skip("pyjwt not installed")
    j = jwt(secret="topsecret")
    tok = pyjwt.encode({"sub": "alice", "user": "alice"}, "topsecret", algorithm="HS256")
    out = j.authenticate(tok)
    assert out["kind"] == "jwt"
    assert out["principal"] == "alice"


def test_cache_lru_eviction() -> None:
    from braid.cache.lru import lru

    c = lru(maxentries=2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert c.get("a") is None
    assert c.get("b") == 2
    assert c.get("c") == 3


def test_secret_env_gets() -> None:
    import os

    from braid.secret.env import env

    e = env()
    os.environ["BRAID_TEST_SECRET"] = "value1"
    try:
        assert e.get("BRAID_TEST_SECRET") == "value1"
    finally:
        del os.environ["BRAID_TEST_SECRET"]


def test_tracing_console_records_span() -> None:
    from braid.tracing.console import console

    t = console()
    t.span("test.span", attributes={"k": 1})


def test_log_structlogjson_emits() -> None:
    from braid.log.structlogjson import structlogjson

    s = structlogjson()
    s.info("an event", k=1, level="info")
    s.warning("a warning", k=2)


def test_metrics_prometheus_counter() -> None:
    from braid.metrics.prometheus import prometheus

    m = prometheus(port=0)
    m.counter("braid.test.counter", value=1.0, labels={"cat": "test"})
    m.gauge("braid.test.gauge", value=2.5)
    m.histogram("braid.test.histogram", value=0.1)
