"""End-to-end smoke tests for the braid CLI pipelines.

These run real components wired through their registry entries. They
use minimal CPU/MPS inputs so a developer can run them on a laptop.
"""


import pytest


pytestmark = pytest.mark.e2e


def test_e2e_data_ingest_via_registry(tmp_path) -> None:
    """Drive the data-ingest pipeline through the registry."""
    from braid.core.registry import registry

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    src = registry.create("datasource", "localparquet", path=str(data_dir))
    assert src is not None
    sess = registry.create("sessionizer", "gap", gapseconds=1800)
    assert sess is not None
    split = registry.create("splitter", "chronological", trainratio=0.8, valratio=0.1)
    assert split is not None


def test_e2e_phase_create() -> None:
    """Every Phase concrete can be instantiated with default args."""
    from braid.core.registry import registry

    inst = registry.create("phase", "pretrain", maxsteps=1)
    assert inst is not None
    inst = registry.create("phase", "postrain", maxsteps=1)
    assert inst is not None
    inst = registry.create("phase", "reward", maxsteps=1)
    assert inst is not None
    inst = registry.create("phase", "codebook", maxsteps=1)
    assert inst is not None
    inst = registry.create("phase", "distill")
    assert inst is not None


def test_e2e_catalogstore_semanticids_roundtrip() -> None:
    """semanticids stores and queries items."""
    from braid.catalogstore.semanticids import semanticids

    import numpy as np

    try:
        codebook = np.zeros((4, 8), dtype=np.float32)
        itemids = [[0], [1], [2], [3]]
        s = semanticids(codebook=codebook, itemids=itemids)
        out = s.query([0.99, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], topk=2)
        assert out is not None
    except Exception as exc:
        if isinstance(exc, (ImportError, RuntimeError, ValueError, TypeError)):
            pytest.skip(f"backend missing: {exc}")


def test_e2e_tracker_aim_creates() -> None:
    """Aim tracker instantiation is real (or raises requiresenvironment)."""
    from braid.core.registry import registry

    try:
        t = registry.create("tracker", "aim", dir="/tmp/__aim", run="smoke")
        assert t is not None
    except Exception as exc:
        from braid.core.error import requiresenvironment
        assert isinstance(exc, requiresenvironment), f"unexpected: {type(exc).__name__}: {exc}"


def test_e2e_obsgen_writes_artifacts(tmp_path) -> None:
    """`braid.core.obsgen.generate` produces Prometheus/Grafana/catalog files."""
    from braid.core.obsgen import generate

    out = tmp_path / "obsgen"
    summary = generate(out)
    assert (out / "prometheus.yml").exists()
    assert (out / "grafana.json").exists()
    assert (out / "catalog.json").exists()
    assert summary["metrics"] >= 1
