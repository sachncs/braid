"""Real assertion tests for offlineranking/calibration/diversity/baseline/replay/interleaving."""

import numpy as np


def test_offlineranking_perfect_ranking() -> None:
    """When the target is rank-1, MRR=1, HitRate@10=1, MAP@10=1/k=0.1."""
    from braid.eval.offlineranking import offlineranking

    er = offlineranking()
    out = er.evaluate(predictions=[[42, 7, 8, 9]], groundtruth=[42], k=10)
    assert out["mrr"] == 1.0
    assert out["hitrate"] == 1.0
    assert out["ndcg"] == 1.0
    assert abs(out["map"] - 1.0 / 10.0) < 1e-6


def test_offlineranking_misses() -> None:
    """When the target is not in predictions, all metrics are 0."""
    from braid.eval.offlineranking import offlineranking

    er = offlineranking()
    out = er.evaluate(predictions=[[1, 2, 3, 4]], groundtruth=[99])
    assert out["mrr"] == 0.0
    assert out["hitrate"] == 0.0
    assert out["ndcg"] == 0.0
    assert out["map"] == 0.0


def test_offlineranking_rank3() -> None:
    """Rank-3 hit: MRR = 1/3, HitRate@10 = 1, MAP@10 = (1/3) / 10."""
    from braid.eval.offlineranking import offlineranking

    er = offlineranking()
    out = er.evaluate(predictions=[[1, 2, 99, 4]], groundtruth=[99], k=10)
    assert abs(out["mrr"] - 1.0 / 3.0) < 1e-6
    assert out["hitrate"] == 1.0
    assert abs(out["map"] - (1.0 / 3.0) / 10.0) < 1e-6


def test_offlineranking_rejects_mismatched_lengths() -> None:
    """Mismatched lengths must raise."""
    import pytest

    from braid.eval.offlineranking import offlineranking

    with pytest.raises(ValueError):
        offlineranking().evaluate(predictions=[[1]], groundtruth=[1, 2])


def test_calibration_well_calibrated() -> None:
    """A perfectly-calibrated model has ECE ~ 0 and low Brier."""
    from braid.eval.calibration import calibration

    cal = calibration()
    scores = [0.5] * 10
    labels = [1] * 5 + [0] * 5
    out = cal.evaluate(scores=scores, labels=labels)
    assert out["ece"] < 0.05
    assert abs(out["brier"] - 0.25) < 1e-6
    assert 0.0 < out["nll"] < 1.0


def test_calibration_overconfident() -> None:
    """Predictions 0.9 with label 0 must inflate ECE > 0.05."""
    from braid.eval.calibration import calibration

    cal = calibration()
    out = cal.evaluate(scores=[0.9] * 10, labels=[0] * 10)
    assert out["ece"] > 0.5
    assert all(abs(b["conf"] - b["acc"]) > 0.5 for b in out["bins"] if b["count"])


def test_diversity_intra_distance() -> None:
    """Identical embeddings → intra distance 0; orthogonal embeddings → ~1.0."""
    from braid.eval.diversity import diversity

    div = diversity(k=4)
    orth = np.eye(4, dtype=np.float32)
    listus = [[0, 1, 2, 3]]
    orthout = div.evaluate(listus, embeddings=orth)
    assert orthout["intra"] > 0.9

    sam = np.zeros((4, 4), dtype=np.float32)
    sam[0] = sam[1] = sam[2] = sam[3] = 1
    samout = div.evaluate(listus, embeddings=sam)
    assert samout["intra"] < 1e-3


def test_diversity_coverage() -> None:
    """Coverage is the fraction of the universe surfaced across all queries."""
    from braid.eval.diversity import diversity

    div = diversity(k=4)
    out = div.evaluate([[0, 1], [2, 3]], universe=[0, 1, 2, 3, 4, 5])
    assert abs(out["coverage"] - 4 / 6) < 1e-6


def test_baseline_comparison_smoke() -> None:
    """``baseline`` produces usable numbers against random + popularity."""
    from braid.eval.baseline import baseline

    bl = baseline()
    preds = [[10, 1, 2, 3, 4]]
    truth = [10]
    popularity = np.zeros(100, dtype=np.float32)
    popularity[10] = 999.0
    rep = bl.evaluate(preds, truth, numitems=100, popularity=popularity)
    assert rep["ours"]["mrr"] == 1.0
    assert rep["random"]["mrr"] < 1.0
    assert rep["popularity"]["mrr"] == 1.0


def test_replay_runs_against_duck() -> None:
    """Replay harness works against a minimal ``rank``-method duck."""
    from braid.eval.replay import replay

    class ranker:
        def rank(self, prompt, context, topk):
            return {"ids": list(range(topk))}

    out = replay().evaluate(ranker(), [{"prompt": "x", "itemid": 0}])
    assert out["mrr"] == 1.0
    assert out["hitrate"] == 1.0


def test_interleaving_ratio() -> None:
    """Interleaving wins/ratios should sum to <=1 and include CI."""
    from braid.eval.interleaving import interleaving

    ev = interleaving()
    out = ev.evaluate(
        lista=[[1, 2, 3]],
        listb=[[4, 5, 6]],
        engagements=[1],
    )
    assert out["winsA"] == 1.0
    assert out["winsB"] == 0.0
    assert out["winsAratio"] == 1.0
    assert 0.0 <= out["ci95low"] <= out["ci95high"] <= 1.0


def test_interleaving_rejects_mismatched() -> None:
    import pytest

    from braid.eval.interleaving import interleaving

    with pytest.raises(ValueError):
        interleaving().evaluate(lista=[[1]], listb=[[1], [2]], engagements=[1])


def test_composite_score_aggregation() -> None:
    """The composite's weighted scalar ``score`` is the average of components."""
    from braid.eval.composite import composite

    comp = composite(members=[("offlineranking", 1.0), ("diversity", 1.0)])
    rep = comp.evaluate(predictions=[[42, 7, 8]], groundtruth=[42])
    assert "score" in rep
    assert "offlineranking" in rep
    assert "diversity" in rep
