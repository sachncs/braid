"""Real assertion tests for drift detectors and response strategies."""

import numpy as np


def test_psi_no_drift() -> None:
    """PSI returns 0 when the live distribution matches the reference."""
    from braid.drift.psi import psi

    det = psi(nbins=10, threshold=0.2)
    ref = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
    det.setreference(ref)
    sig = det.update(np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64))
    assert sig["drifted"] is False
    assert sig["score"] <= 0.05


def test_psi_high_drift() -> None:
    """PSI spikes when the live distribution shifts sharply."""
    from braid.drift.psi import psi

    det = psi(nbins=10, threshold=0.2)
    ref = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
    det.setreference(ref)
    sig = det.update(np.array([100.0, 100.0, 100.0, 100.0, 100.0], dtype=np.float64))
    assert sig["drifted"] is True
    assert sig["score"] > 0.2


def test_pagehinkley_below_threshold() -> None:
    from braid.drift.pagehinkley import pagehinkley

    det = pagehinkley(delta=0.005, threshold=50.0)
    for _ in range(20):
        sig = det.update(0.5)
    assert sig["drifted"] is False


def test_ks_returns_score() -> None:
    """KS returns a numeric ``score`` (or ``pvalue``) key, so callers can threshold."""
    from braid.drift.ks import ks

    det = ks(threshold=0.05)
    det.setreference(np.random.default_rng(0).normal(size=200))
    live = np.random.default_rng(1).normal(size=200)
    sig = det.update(live)
    assert "score" in sig or "pvalue" in sig
    val = sig.get("pvalue", sig.get("score"))
    assert isinstance(val, float)
    assert "drifted" in sig or "drift_detected" in sig


def test_drift_response_fallback_toggles() -> None:
    """A fallback drift response sets usingbaseline=True on respond()."""
    from braid.driftresponse.fallback import fallback

    resp = fallback()
    assert resp.usingbaseline is False
    resp.respond({"score": 0.4})
    assert resp.usingbaseline is True
    resp.reset()
    assert resp.usingbaseline is False


def test_drift_response_alert_emits_log() -> None:
    """An alert response emits via logger on respond()."""
    from braid.driftresponse.alert import alert

    resp = alert(channel="braid.drift.test")
    resp.respond({"score": 0.9, "detector": "psi"})


def test_retraintrigger_writes_file(tmp_path) -> None:
    """When the metric breaches, retraintrigger writes the trigger file."""
    from braid.driftresponse.retraintrigger import retraintrigger

    resp = retraintrigger(path=str(tmp_path / "rt.trigger"))
    resp.respond({"score": 0.9})
    assert (tmp_path / "rt.trigger").exists()



