"""Evaluator tests."""

def test_offlineranking_metrics() -> None:
    """offlineranking returns mrr/ndcg/etc."""
    import braid

    ev = braid.registry.create("eval", "offlineranking")
    predictions = [[3, 1, 2], [1, 2, 3]]
    groundtruth = [1, 1]
    result = ev.evaluate(predictions, groundtruth)
    assert "mrr" in result
    assert "ndcg" in result


def test_interleaving_interleave() -> None:
    """Team-draft interleaving yields length-merged list + owners."""
    import braid

    ie = braid.registry.create("eval", "interleaving")
    combined, owners = ie.interleave([1, 2, 3], [4, 5, 6])
    assert len(combined) == 6
    assert set(owners) == {"A", "B"}


def test_baseline_compare() -> None:
    """baseline returns ours + random + popularity metrics."""
    import numpy as np

    import braid

    ev = braid.registry.create("eval", "baseline")
    rep = ev.evaluate([[1, 2, 3], [2, 3, 4]], [1, 2], numitems=10, popularity=np.array([1] * 10, dtype=np.float32))
    assert "ours" in rep
    assert "random" in rep
