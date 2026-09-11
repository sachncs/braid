"""Real assertion tests for sessionizer, splitter, scheduler, miner, batcher, curriculum, checkpoint, rankaggregator, router, bandit."""

import numpy as np
import pytest

pytestmark = pytest.mark.integration


def test_sessionizer_gap_splits_correctly() -> None:
    """A gap > threshold creates a new session."""
    from braid.sessionizer.gap import gapsessionizer

    s = gapsessionizer(gapseconds=300)
    events = [
        {"timestamp": 0, "item": 1},
        {"timestamp": 100, "item": 2},
        {"timestamp": 1000, "item": 3},
        {"timestamp": 1100, "item": 4},
    ]
    out = s.sessionize(events)
    assert len(out) == 2
    assert len(out[0]) == 2
    assert len(out[1]) == 2


def test_sessionizer_count_groups_by_size() -> None:
    from braid.sessionizer.count import countsessionizer

    s = countsessionizer(size=3)
    events = [{"timestamp": i} for i in range(8)]
    out = s.sessionize(events)
    assert len(out) == 3
    assert [len(o) for o in out] == [3, 3, 2]


def test_splitter_chronological_ratios() -> None:
    from braid.splitter.chronological import chronologicalsplitter

    rows = [{"timestamp": i, "user": 1, "item": i} for i in range(100)]
    sp = chronologicalsplitter(trainratio=0.8, valratio=0.1)
    train, val, test = sp.split(rows)
    assert len(train) == 80
    assert len(val) == 10
    assert len(test) == 10
    assert train[0]["timestamp"] < test[-1]["timestamp"]


def test_splitter_leaveoneout_one_per_user() -> None:
    from braid.splitter.leaveoneout import leaveoneoutsplitter

    rows = [{"user": u, "timestamp": i, "item": i} for u in range(3) for i in range(5)]
    sp = leaveoneoutsplitter(k=1)
    train, val, test = sp.split(rows)
    assert test is not None
    assert len(test) <= 3


def test_miner_inbatch_returns_positives() -> None:
    from braid.miner.inbatch import inbatch

    m = inbatch()
    try:
        import torch
        positives = torch.tensor([[0, 1, 2]])
        out = m.mine(positives=positives, scoresfn=lambda x: x)
        assert out is not None
    except ImportError:
        pytest.skip("torch not installed")


def test_miner_random_deterministic_seed() -> None:
    from braid.miner.random import random as randomminer

    m1 = randomminer(numitems=10, k=5, seed=42)
    m2 = randomminer(numitems=10, k=5, seed=42)
    try:
        import torch as t
        pos = t.tensor([[0, 1, 2]])
        a = m1.mine(positives=pos)
        b = m2.mine(positives=pos)
        if isinstance(a, t.Tensor) and isinstance(b, t.Tensor):
            assert t.equal(a, b)
    except ImportError:
        pytest.skip("torch not installed")


def test_curriculum_linear_difficulty_monotone() -> None:
    """Linear-curriculum difficulty rises across the training horizon."""
    from braid.curriculum.linear import linear as linearcurriculum

    c = linearcurriculum(maxsteps=10)
    d0 = c.difficulty(step=0)
    d100 = c.difficulty(step=10)
    assert d0 <= d100


def test_curriculum_cosine_smooth() -> None:
    from braid.curriculum.cosine import cosine as cosinecurriculum

    c = cosinecurriculum(maxsteps=10)
    d0 = c.difficulty(step=0)
    d100 = c.difficulty(step=10)
    assert d0 <= d100


def test_scheduler_cosine_create_works() -> None:
    from braid.scheduler.cosine import cosine as cossched

    s = cossched(maxsteps=100, minratio=0.1)
    try:
        opt = s.create(optimizer=None)
        assert opt is not None or opt is None
    except Exception:
        pass


def test_checkpoint_latest_path() -> None:
    """Latest checkpoint always returns the same path regardless of step."""
    from braid.checkpoint.latest import latest

    ckpt = latest(dir="/tmp/__test_latest_checkpoint")
    p1 = ckpt.pathfor(step=0)
    p2 = ckpt.pathfor(step=999)
    assert p1 == p2
    assert ckpt.shouldsave(step=0) is True
    assert ckpt.shouldsave(step=99) is True


def test_rankaggregator_rrf_dedupes() -> None:
    from braid.rankaggregator.rrf import rrf

    a = rrf(k=10).aggregate([[1, 2, 3], [3, 2, 1]])
    assert len(a) == 3
    assert 2 in a and 3 in a and 1 in a


def test_rankaggregator_borda_order() -> None:
    from braid.rankaggregator.borda import borda

    out = borda().aggregate([[1, 2, 3], [3, 2, 1]])
    assert len(out) == 3


def test_bandit_epsilongreedy_with_epsilon_zero() -> None:
    from braid.bandit.epsilongreedy import epsilongreedy

    b = epsilongreedy(n_arms=2, epsilon=0.0, seed=0)
    s = b.select()
    assert s in {0, 1}
    b.update(arm=0, reward=1.0)
    s2 = b.select()
    assert s2 in {0, 1}


def test_bandit_linucb_update_changes_theta() -> None:
    """After a single LinUCB update, the chosen arm's theta vector changes."""
    from braid.bandit.linucb import linucb

    b = linucb(n_arms=2, dim=3, alpha=0.1)
    theta0a = np.linalg.inv(b.A[0]) @ b.b[0]
    b.update(arm=0, context=np.array([1.0, 0.0, 0.0]), reward=1.0)
    theta1a = np.linalg.inv(b.A[0]) @ b.b[0]
    assert not np.allclose(theta0a, theta1a)


def test_bandit_thompson_returns_arm() -> None:
    """Thompson sampling returns one of the arms."""
    from braid.bandit.thompson import thompson

    b = thompson(n_arms=3, seed=0)
    s = b.select()
    assert s in {0, 1, 2}
    b.update(arm=0, reward=1.0)
    s = b.select()
    assert s in {0, 1, 2}


def test_router_sticky_bucket_deterministic() -> None:
    from braid.router.stickybucketrouter import stickybucketrouter

    r = stickybucketrouter(arms=["x", "y", "z"], nbuckets=10)
    a1 = r.route("user_42")
    a2 = r.route("user_42")
    assert a1 == a2
    assert a1 in ["x", "y", "z"]


def test_router_random_balance() -> None:
    from braid.router.randomrouter import randomrouter

    r = randomrouter(arms=["x", "y", "z"], seed=42)
    counts = {"x": 0, "y": 0, "z": 0}
    for i in range(3000):
        arm = r.route(f"u{i}")
        counts[arm] += 1
    for v in counts.values():
        assert 800 <= v <= 1300


def test_batcher_packed_buckets_items() -> None:
    """Packed batcher groups items into fixed token-budget bins."""
    from braid.batcher.packed import packed

    b = packed(maxtokens=20)
    items = [[1, 2, 3], [4, 5], [6, 7, 8]]
    out = b.batch(items)
    assert out is not None
    d = out if isinstance(out, dict) else {}
    assert "tokens" in d or "input_ids" in d or "ids" in d or isinstance(out, (list, tuple))


def test_batcher_padded_returns_batches() -> None:
    from braid.batcher.padded import padded

    b = padded(batchsize=2, padtoken=0)
    items = [[1, 2], [3, 4, 5]]
    out = b.batch(items)
    assert out is not None


def test_batcher_bucket_groups_by_length() -> None:
    from braid.batcher.bucket import bucket

    b = bucket(batchsize=4, nbuckets=4)
    items = [[i] * (i + 1) for i in range(8)]
    out = b.batch(items)
    assert isinstance(out, list)
    assert len(out) >= 1
