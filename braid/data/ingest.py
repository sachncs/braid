"""End-to-end ingest pipeline composed of registered concretes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from braid.core.registry import registry
from braid.core.logging import getlogger


def ingest(configpath: str) -> dict[str, Any]:
    """Run the full ingest pipeline from a config file.

    Args:
        configpath: path to a YAML config with at least ``datasource``,
            ``sessionizer``, ``splitter``, ``metadata``, ``datasink``.

    Returns:
        A summary dict with ``train``, ``val``, ``test`` row counts and
        the resolved concrete names.
    """
    log = getlogger("braid.data.ingest")
    cfg = yaml.safe_load(Path(configpath).read_text())
    src = registry.create("datasource", cfg["datasource"]["type"], **{k: v for k, v in cfg["datasource"].items() if k != "type"})
    sess = registry.create("sessionizer", cfg["sessionizer"]["type"], **{k: v for k, v in cfg["sessionizer"].items() if k != "type"})
    split = registry.create("splitter", cfg["splitter"]["type"], **{k: v for k, v in cfg["splitter"].items() if k != "type"})
    sink = registry.create("datasink", cfg["datasink"]["type"], **{k: v for k, v in cfg["datasink"].items() if k != "type"})
    rows = list(src.read())
    log.info("ingest.read", rows=len(rows), source=type(src).__name__)
    sessions = sess.sessionize(rows)
    log.info("ingest.sessionized", sessions=len(sessions), type=type(sess).__name__)
    train, val, test = split.split(rows)
    log.info("ingest.split", train=len(train), val=len(val), test=len(test))
    sink.write(rows)
    return {
        "totalsessions": len(sessions),
        "train": len(train),
        "val": len(val),
        "test": len(test),
        "datasource": type(src).__name__,
        "sessionizer": type(sess).__name__,
        "splitter": type(split).__name__,
        "datasink": type(sink).__name__,
    }
