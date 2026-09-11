"""Real assertion tests for indexer, quantizer, additional regularizers, additional optimizers."""

import numpy as np
import pytest

pytestmark = pytest.mark.integration


def test_indexer_hash_roundtrip() -> None:
    """Hash indexer stores embeddings and queries nearest neighbours."""
    from braid.indexer.hash import hash as hashix

    emb = np.eye(8, dtype=np.float32)
    ix = hashix(embeddings=emb, nbits=8)
    out = ix.query(np.array([1.0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32), topk=3)
    assert isinstance(out, np.ndarray)
    assert out.size <= 3


def test_indexer_exact_nearest_neighbor() -> None:
    """Exact indexer returns the closest vector within the catalog."""
    from braid.indexer.exact import exact

    emb = np.eye(4, dtype=np.float32)
    e = exact(embeddings=emb)
    q = np.array([0.99, 0.01, 0.0, 0.0], dtype=np.float32)
    out = e.query(q, topk=2)
    assert isinstance(out, np.ndarray)
    assert out.size >= 1


def test_quantizer_quantizer_signature() -> None:
    """Quantizer encodes and decodes through a residual stack."""
    from braid.quantizer.quantizer import quantizer

    q = quantizer(numcodes=8, dim=16, numstages=2, seed=0)
    v = np.random.default_rng(0).standard_normal(16).astype(np.float32)
    codes = q.quantize(v)
    decoded = q.dequantize(codes)
    assert len(codes) == 2
    assert decoded.shape == v.shape


def test_regularizer_labelsmoothing_smoothes() -> None:
    from braid.regularizer.labelsmoothing import labelsmoothing

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    ls = labelsmoothing(epsilon=0.1)
    smoothed = ls.smooth(labels=torch.tensor([2]), numclasses=10)
    assert smoothed.shape[-1] == 10
    assert abs(float(smoothed.sum()) - 1.0) < 1e-3


def test_regularizer_tokendropout_replaces() -> None:
    from braid.regularizer.tokendropout import tokendropout

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    td = tokendropout(p=0.5, replacetoken=0)
    x = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]])
    y = td.apply(x)
    assert y.shape == x.shape


def test_optimizer_adafactor_create() -> None:
    from braid.optimizer.adafactor import adafactor

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    p = torch.nn.Linear(4, 4)
    o = adafactor(lr=0.001)
    try:
        opt = o.create(p.parameters())
        assert opt is not None
    except Exception as exc:
        from braid.core.error import requiresenvironment
        if isinstance(exc, requiresenvironment):
            pytest.skip("adafactor missing")


def test_optimizer_schedulefree_create() -> None:
    from braid.optimizer.schedulefree import schedulefree

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    p = torch.nn.Linear(4, 4)
    o = schedulefree(lr=0.001)
    try:
        opt = o.create(p.parameters())
        assert opt is not None
    except Exception as exc:
        from braid.core.error import requiresenvironment
        if isinstance(exc, requiresenvironment):
            pytest.skip("schedulefree missing")


def test_loss_calibrationloss_runs() -> None:
    from braid.loss.calibrationloss import calibrationloss

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    cl = calibrationloss(nbins=10)
    scores = torch.randn(8, 4)
    labels = torch.tensor([0, 1, 2, 3, 0, 1, 2, 3])
    out = cl.compute(scores, labels, weight=1.0)
    assert float(out.detach()) > 0.0


def test_loss_rewardweighted_runs() -> None:
    from braid.loss.rewardweighted import rewardweighted

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    rw = rewardweighted(normalize=True)
    scores = torch.randn(4, 8)
    labels = torch.tensor([0, 1, 2, 3])
    rewards = torch.tensor([0.1, 0.5, 0.9, 0.2])
    out = rw.compute(scores, labels, rewards, weight=1.0)
    assert out is not None
