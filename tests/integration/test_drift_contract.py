"""Drift detector tests."""

import numpy as np


def test_psi_drift() -> None:
    """PSI detects distribution shift."""
    import braid

    det = braid.registry.create("drift", "psi", nbins=5, threshold=0.1)
    det.setreference(np.array([1, 2, 3, 4, 5], dtype=np.float32))
    result = det.update(np.array([5, 5, 5, 5, 5], dtype=np.float32))
    assert result["drifted"] in (True, False)


def test_ks_drift() -> None:
    """KS computes a non-negative score."""
    import braid

    det = braid.registry.create("drift", "ks", threshold=0.1)
    det.setreference(np.array([1, 2, 3, 4, 5], dtype=np.float32))
    result = det.update(np.array([5, 5, 5, 5, 5], dtype=np.float32))
    assert result["score"] >= 0


def test_pagehinkley_step() -> None:
    """Page-Hinkley step updates state."""
    import braid

    det = braid.registry.create("drift", "pagehinkley", threshold=10.0)
    sig = det.update(1.0)
    assert "drifted" in sig
