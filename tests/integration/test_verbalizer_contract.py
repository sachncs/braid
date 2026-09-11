"""Verbalizer tests."""

import pytest

pytestmark = pytest.mark.integration


def test_eventsignal_render() -> None:
    """The eventsignal verbalizer produces non-empty text."""
    import braid

    v = braid.registry.create("verbalizer", "eventsignal", budget=10)
    context = {
        "user": "u1",
        "history": [
            {"userid": "u1", "itemid": 1, "kind": "play", "duration": 120.0},
            {"userid": "u1", "itemid": 2, "kind": "thumbup", "duration": 0.0},
        ],
        "candidates": [3, 4, 5],
    }
    out = v.render(context)
    assert isinstance(out, str)
    assert "rank" in out.lower()


def test_truncate_signalweighted() -> None:
    """Signal-weighted truncation keeps high-signal events."""
    from braid.truncation.signalweighted import signalweighted

    events = [
        {"duration": 100, "kind": "play"},
        {"duration": 9999, "kind": "play"},
        {"duration": 1, "kind": "click"},
    ]
    kept = signalweighted(budget=2).fit(events)
    assert len(kept) == 2


def test_template_jinja2() -> None:
    """Jinja2 template renders."""
    import braid

    t = braid.registry.create("template", "jinja2", template="{{ x }}")
    assert t.render(x="hi") == "hi"


def test_template_fstring() -> None:
    """F-string template renders."""
    import braid

    t = braid.registry.create("template", "fstring", template="hi {x}")
    assert t.render(x="there") == "hi there"


def test_tokenizer_approx() -> None:
    """Approximate token count is positive for non-empty text."""
    import braid

    c = braid.registry.create("tokencounter", "approxcount")
    n = c.count("hello world, this is a test of approximate token counting")
    assert n > 0
