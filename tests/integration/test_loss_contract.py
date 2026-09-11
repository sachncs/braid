"""Loss conformance tests."""

import pytest

pytestmark = pytest.mark.integration


def test_rankingce_smoke() -> None:
    """Cross-entropy smoke test."""
    pytest.importorskip("torch")
    import torch

    import braid

    loss = braid.registry.create("loss", "rankingce")
    scores = torch.randn(2, 5, requires_grad=True)
    labels = torch.tensor([1, 3])
    val = loss.compute(scores, labels)
    assert val.item() > 0


def test_diversity_entropy_regularizer() -> None:
    """Diversity entropy regularizer."""
    pytest.importorskip("torch")
    import torch

    import braid

    reg = braid.registry.create("loss", "diversityentropy")
    scores = torch.randn(2, 10, requires_grad=True)
    val = reg.compute(scores, weight=0.5)
    assert val.item() <= 0  # negative entropy is non-positive


def test_braidedloss_composes() -> None:
    """A braided loss with a single term computes without error."""
    pytest.importorskip("torch")
    import torch

    import braid

    braidloss = braid.registry.create("loss", "braidedloss", terms=[("rankingce", 1.0)])
    out = {"scores": torch.randn(2, 5, requires_grad=True)}
    batch = {"labels": torch.tensor([1, 3]), "inputids": torch.tensor([[1, 2]])}
    val = braidloss.compute(out, batch)
    assert val.requires_grad
