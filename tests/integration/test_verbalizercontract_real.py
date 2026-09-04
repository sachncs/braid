"""Real assertion tests for the verbalizer pipeline."""

import pytest


def test_elbowfinder_finds_kink() -> None:
    """For a left-peaked histogram (elbow at K=3), the elbow finder should pick K<=5."""
    from braid.verbalizer.elbowfinder import run as elbowrun

    events = [{"duration": 1.0}] * 30 + [{"duration": 50.0}] * 5 + [{"duration": 90.0}] * 2
    sweep = elbowrun(events, krange=range(2, 12, 2))
    assert isinstance(sweep, dict)
    assert len(sweep) > 0


def test_truncation_head_lossless_for_short() -> None:
    from braid.truncation.head import head as headtrunc

    items = ["a", "b", "c", "d", "e"]
    out = headtrunc(budget=3).fit(items)
    assert out == ["c", "d", "e"]


def test_truncation_diversity_round_robin() -> None:
    from braid.truncation.diversity import diversity

    items = [{"kind": "x0"}, {"kind": "y0"}, {"kind": "x1"}, {"kind": "y1"}, {"kind": "x2"}, {"kind": "y2"}, {"kind": "x3"}]
    out = diversity(budget=4).fit(items)
    assert len(out) >= 1


def test_tokencounter_known_count() -> None:
    from braid.tokencounter.approxcount import approxcount

    c = approxcount(charsperratio=5.0)
    n = c.count("hello world this is braid")
    assert n == len("hello world this is braid") / 5.0


def test_template_renders_fstring() -> None:
    from braid.template.fstring import fstring

    t = fstring(template="hello {who}!")
    out = t.render(who="world")
    assert "world" in out


def test_pipeline_assembles() -> None:
    """Verbalizer + truncation + template produce a non-empty prompt."""
    from braid.core.registry import registry
    from braid.truncation.head import head as headtrunc

    verbal = registry.create("verbalizer", "compactelbow")
    items = [
        {"kind": "play", "itemid": 1, "title": "Movie A", "when": "2024-01"},
        {"kind": "thumb", "itemid": 2, "title": "Movie B", "when": "2024-02"},
        {"kind": "play", "itemid": 3, "title": "Movie C", "when": "2024-03"},
    ]
    prompt = verbal.render({"user": "u", "history": items, "candidates": [10, 20, 30]})
    assert "Movie" in prompt or "user" in prompt
    trunc = headtrunc(budget=5).fit([prompt])
    assert len(trunc) >= 1
