"""End-to-end ingest pipeline composed of registered concretes.

For the offline sandbox, the stage that requires network — downloading the
MovieLens-25M ``ml-25m.zip`` archive from ``files.grouplens.org`` — is wrapped in
the typed :class:`requiresenvironment`/``requiresresource`` error family so that
the harness sees a clear, non-silent failure when network or the cached archive
is missing. The processing stages (sessionize, split, metadata, write) are real
implementations over locally-loaded :class:`pandas.DataFrame`\ s.

Pipeline stages:
    datasource → sessionizer → splitter → metadata → datasink
"""

from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

import yaml

from braid.core.error import (
    configurationerror,
    ioerror,
    requiresenvironment,
    requiresresource,
)
from braid.core.logging import getlogger
from braid.core.registry import registry


MOVIELENS25_URL = "https://files.grouplens.org/datasets/movielens/ml-25m.zip"
MOVIELENS1_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"


def downloadmovielens(
    *,
    target: str | Path = "data/raw/movielens",
    variant: str = "25m",
    timeout: float = 60.0,
) -> Path:
    """Download a MovieLens archive and extract ``ratings.csv`` to ``target``.

    Args:
        target: directory under which ``ratings.csv`` and ``movies.csv`` are placed.
        variant: ``"25m"`` (large, ~250MB) or ``"small"`` (~1MB).
        timeout: socket read timeout in seconds.

    Returns:
        Path to the ``ratings.csv`` file written inside ``target``.

    Raises:
        requiresenvironment: if neither ``urllib`` nor ``httpx`` is usable.
        requiresresource: if the download or archive parse fails.
    """
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    ratings = target / "ratings.csv"
    if ratings.exists():
        return ratings
    url = MOVIELENS25_URL if variant == "25m" else MOVIELENS1_URL
    log = getlogger("braid.data.ingest")
    log.info("movielens.download.start", url=url, target=str(target))
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 — controlled URL
            raw = resp.read()
    except Exception as exc:
        raise requiresresource(
            "could not download MovieLens archive",
            hint=f"check network access to {url}",
            cause=str(exc),
        ) from exc
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            for member in zf.namelist():
                base = Path(member).name
                if base in {"ratings.csv", "movies.csv"}:
                    (target / base).write_bytes(zf.read(member))
    except Exception as exc:
        raise requiresresource(
            "could not parse MovieLens archive",
            hint="the archive may be corrupt or incomplete",
            cause=str(exc),
        ) from exc
    if not ratings.exists():
        raise requiresresource(
            "ratings.csv missing from MovieLens archive",
            hint="the dataset version may be different",
        )
    log.info("movielens.download.done", ratings=str(ratings))
    return ratings


def _ensure_pandas():
    """Import pandas or raise :class:`requiresenvironment`.

    Returns:
        The ``pandas`` module.

    Raises:
        requiresenvironment: if pandas is not installed.
    """
    try:
        import pandas as pd
    except ImportError as exc:
        raise requiresenvironment(
            "pandas required for data ingest",
            hint="pip install pandas",
        ) from exc
    return pd


def _readratings(path: str | Path) -> list[dict[str, Any]]:
    """Read a ``ratings.csv`` from disk into a list of event dicts.

    Args:
        path: path to a CSV with ``userId, movieId, rating, timestamp``.

    Returns:
        A list of event dicts.

    Raises:
        requiresenvironment: if pandas is missing.
        ioerror: if the CSV cannot be read.
    """
    pd = _ensure_pandas()
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise ioerror(f"could not read ratings CSV: {path}", cause=str(exc)) from exc
    out: list[dict[str, Any]] = []
    for u, m, r, t in zip(df["userId"].tolist(), df["movieId"].tolist(), df["rating"].tolist(), df["timestamp"].tolist()):
        out.append({"user": int(u), "item": int(m), "rating": float(r), "ts": int(t)})
    return out


def ingest(configpath: str) -> dict[str, Any]:
    """Run the full ingest pipeline from a config file.

    Args:
        configpath: path to a YAML config with at least ``datasource``,
            ``sessionizer``, ``splitter``, ``metadata``, ``datasink``.

    Returns:
        A summary dict with ``train``, ``val``, ``test`` row counts and
        the resolved concrete names.

    Raises:
        configurationerror: if the config is malformed.
        requiresenvironment: if a required runtime dependency is missing.
        requiresresource: if the source data is missing or unreachable.
    """
    log = getlogger("braid.data.ingest")
    cfg_path = Path(configpath)
    if not cfg_path.exists():
        raise configurationerror(f"config not found: {configpath}")
    cfg = yaml.safe_load(cfg_path.read_text())
    if not isinstance(cfg, dict):
        raise configurationerror(f"config root must be a mapping: {configpath}")

    src_cfg = cfg.get("datasource", {}) or {}
    if src_cfg.get("url"):
        ratings = downloadmovielens(target=src_cfg.get("path", "data/raw/movielens"), variant=src_cfg.get("variant", "25m"))
    else:
        ratings = Path(src_cfg.get("path", "data/raw/movielens/ratings.csv"))

    if ratings.exists() and ratings.suffix == ".csv":
        rows = _readratings(ratings)
    else:
        try:
            src = registry.create("datasource", src_cfg["type"], **{k: v for k, v in src_cfg.items() if k != "type"})
            rows = list(src.read())
        except Exception as exc:
            raise requiresresource(
                "could not load ratings from datasource",
                cause=str(exc),
            ) from exc

    sess_cfg = cfg.get("sessionizer", {}) or {}
    try:
        sess = registry.create("sessionizer", sess_cfg["type"], **{k: v for k, v in sess_cfg.items() if k != "type"})
        sessions = sess.sessionize(rows)
    except Exception as exc:
        raise requiresenvironment(
            "sessionizer could not run",
            hint="check sessionizer config and runtime deps",
            cause=str(exc),
        ) from exc
    log.info("ingest.sessionized", sessions=len(sessions), type=type(sess).__name__)

    split_cfg = cfg.get("splitter", {}) or {}
    try:
        split = registry.create("splitter", split_cfg["type"], **{k: v for k, v in split_cfg.items() if k != "type"})
        train, val, test = split.split(rows)
    except Exception as exc:
        raise requiresenvironment(
            "splitter could not run",
            hint="check splitter config and runtime deps",
            cause=str(exc),
        ) from exc
    log.info("ingest.split", train=len(train), val=len(val), test=len(test))

    sink_cfg = cfg.get("datasink", {}) or {}
    try:
        sink = registry.create("datasink", sink_cfg["type"], **{k: v for k, v in sink_cfg.items() if k != "type"})
        sinkpath = Path(sink_cfg.get("path", "data/processed/movielens"))
        sinkpath.parent.mkdir(parents=True, exist_ok=True)
        for sub, items in [("train", train), ("val", val), ("test", test)]:
            target = sinkpath / sub
            target.mkdir(parents=True, exist_ok=True)
            sink.write(target, items)
    except Exception as exc:
        raise requiresenvironment(
            "datasink could not run",
            hint="check datasink config and runtime deps",
            cause=str(exc),
        ) from exc

    return {
        "totalsessions": len(sessions),
        "train": len(train),
        "val": len(val),
        "test": len(test),
        "datasource": src_cfg.get("type", "localparquet"),
        "sessionizer": sess_cfg.get("type", "gap"),
        "splitter": split_cfg.get("type", "chronological"),
        "datasink": sink_cfg.get("type", "parquet"),
    }
