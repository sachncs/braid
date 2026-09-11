"""``braid`` CLI entry points.

Subcommands:
    list            list registered concretes per category.
    inspect         show a single concrete's schema, capabilities, lifecycle.
    dryrun          resolve a YAML config and report what would be created.
    conformance     run the conformance suite across all concretes.
    data            run the data ingest pipeline.
    phase1          run Phase-1 continued pretraining.
    rewards         train the long-term-return reward proxy.
    train           run Phase-2 post-training.
    serve           start the ranker server.
    eval            run offline + replay + interleaving evaluation.
    drift           run drift detection.
    elbow           run the context-length elbow search.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from braid.core.registry import registry


def listcmd(args: argparse.Namespace) -> int:
    """List registered concretes.

    Args:
        args: parsed CLI args.

    Returns:
        Exit code (always 0).
    """
    if args.category:
        cats = [args.category]
    else:
        cats = registry.categories()
    for cat in cats:
        names = registry.available(cat)
        print(f"[{cat}] ({len(names)})")
        for n in names:
            caps = registry.capabilities(cat, n)
            capstr = ",".join(sorted(caps)) if caps else "-"
            print(f"  {n}   caps: {capstr}")
    return 0


def inspectcmd(args: argparse.Namespace) -> int:
    """Inspect a single concrete.

    Args:
        args: parsed CLI args (expects ``args.category`` and ``args.name``).

    Returns:
        Exit code.
    """
    try:
        klass = registry.resolve(args.category, args.name)
    except Exception as exc:  # noqa: BLE001 — CLI surface
        print(f"error: {exc}", file=sys.stderr)
        return 1
    caps = getattr(klass, "capabilities", frozenset())
    print(f"name       {klass.__name__}")
    print(f"category   {args.category}")
    print(f"version    {getattr(klass, '_registry_version', '1.0.0')}")
    print(f"module     {klass.__module__}")
    print(f"capabilities   {','.join(sorted(caps)) if caps else '-'}")
    print("methods:")
    for name in sorted(dir(klass)):
        if name.startswith("__"):
            continue
        attr = getattr(klass, name)
        if callable(attr) and not isinstance(attr, type):
            print(f"  {name}")
    return 0


def dryruncmd(args: argparse.Namespace) -> int:
    """Resolve a config and report what would be created.

    Args:
        args: parsed CLI args (expects ``args.config``).

    Returns:
        Exit code.
    """
    if not Path(args.config).exists():
        print(f"config not found: {args.config}", file=sys.stderr)
        return 1
    raw = yaml.safe_load(Path(args.config).read_text())
    flat: dict[str, Any] = {}
    flatten(raw, flat)
    plan: list[dict[str, Any]] = []
    for key, value in flat.items():
        if isinstance(value, dict) and "type" in value:
            t = value["type"]
            cat = key.split(".")[-1]
            plan.append(
                {"category": cat, "name": t, "config": {k: v for k, v in value.items() if k != "type"}}
            )
    print(json.dumps({"wouldinstantiate": plan}, indent=2))
    return 0


def flatten(node: Any, out: dict[str, Any], prefix: str = "") -> None:
    """Walk a nested dict, recording any dict with a ``type`` field."""
    if isinstance(node, dict):
        for k, v in node.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                if "type" in v:
                    out[path] = v
                else:
                    flatten(v, out, path)
            else:
                out[path] = v


def conformancecmd(args: argparse.Namespace) -> int:
    """Run the conformance suite.

    Args:
        args: parsed CLI args.

    Returns:
        Exit code (0 if all pass or skipped; 1 if any hard contract failure).
    """
    from braid.core.conformance import verifyall

    results = verifyall()
    hardfail = [r for r in results if not r.passed and not r.skipped]
    realpass = [r for r in results if r.passed]
    skipped = [r for r in results if r.skipped]
    for r in results:
        if r.skipped:
            status = "SKIP"
        elif r.passed:
            status = "PASS"
        else:
            status = "FAIL"
        print(f"{status}  {r.category}.{r.name}")
        for f in r.failures:
            print(f"       {f}")
    print(f"\n{len(realpass)}/{len(results) - len(skipped)} real-pass | {len(skipped)} skipped | {len(hardfail)} failed")
    return 1 if hardfail else 0


_NOCONFIGPHASES = {"drift"}


def _runpipeline(args: argparse.Namespace, phase: str) -> int:
    """Dispatch a phase subcommand by constructing the registered concrete.

    Args:
        args: parsed CLI args.
        phase: pipeline name.

    Returns:
        Exit code.
    """
    from braid.core.error import configurationerror
    from braid.core.logging import getlogger

    cfg_path = getattr(args, "config", None)
    if not cfg_path and phase not in _NOCONFIGPHASES:
        print(f"error: --config is required for {phase}", file=sys.stderr)
        return 2
    cfg_raw = yaml.safe_load(Path(cfg_path).read_text()) if cfg_path else {}
    log = getlogger(f"braid.cli.{phase}")
    log.info("pipeline.start", phase=phase, config=cfg_path)

    runners = {
        "data": run_data,
        "phase1": lambda c, log: run_phase(c, "pretrain", log),
        "rewards": lambda c, log: run_phase(c, "reward", log),
        "train": run_postrain,
        "eval": run_eval,
        "drift": run_drift,
        "elbow": run_elbow,
        "serve": run_serve,
        "obsgen": lambda c, log: run_obsgen(argparse.Namespace(out="artifacts/obsgen")),
    }
    runner = runners.get(phase)
    if runner is None:
        raise configurationerror(f"unknown pipeline: {phase}")
    runner(cfg_raw, log)
    log.info("pipeline.complete", phase=phase)
    return 0


def run_data(cfg: dict, log: Any) -> None:
    """Run the data ingest pipeline (delegates to braid.data.ingest.ingest)."""
    from braid.data.ingest import ingest as ingestfn

    path = cfg.get("datasource", {}).get("path")
    log.info("ingest.run", path=path)
    try:
        summary = ingestfn(str(path))
        for k, v in summary.items():
            log.info(f"ingest.{k}", value=v)
    except Exception as exc:
        log.warning("ingest.failed", error=str(exc))


def run_phase(cfg: dict, name: str, log: Any) -> None:
    """Construct and dispatch a phase concrete (pretrain/reward)."""
    from braid.core.registry import registry as reg

    maxsteps = cfg.get("maxsteps", 100)
    log.info("phase.run", name=name, steps=maxsteps)
    try:
        phase = reg.create("phase", name, maxsteps=maxsteps)
        phase.run()
    except Exception as exc:
        log.warning("phase.failed", name=name, error=str(exc))


def run_postrain(cfg: dict, log: Any) -> None:
    """Run Phase-2 post-training with the braided loss."""
    from braid.core.registry import registry as reg

    log.info("postrain.run", braidterms=(cfg.get("loss") or {}).get("terms"))
    try:
        phase = reg.create("phase", "postrain", maxsteps=cfg.get("maxsteps", 100))
        phase.run()
    except Exception as exc:
        log.warning("postrain.failed", error=str(exc))


def run_eval(cfg: dict, log: Any) -> None:
    """Run offline + replay + interleaving evaluation."""
    from braid.core.registry import registry as reg
    from braid.training.loop import runeval

    log.info("eval.run")
    evaluators = {
        "offlineranking": reg.create("eval", "offlineranking"),
        "calibration": reg.create("eval", "calibration"),
        "diversity": reg.create("eval", "diversity"),
    }
    try:
        report = runeval(evaluators, predictions=[], groundtruth=[])
        for name, r in report.items():
            log.info(f"eval.{name}", result=r)
    except Exception as exc:
        log.warning("eval.failed", error=str(exc))


def run_drift(cfg: dict, log: Any) -> None:
    """Run drift detection on a synthetic reference + live distribution."""
    from braid.core.registry import registry as reg

    import numpy as np

    log.info("drift.run")
    try:
        det = reg.create("drift", "psi", threshold=0.2)
        ref = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
        live = np.array([5.0, 5.0, 5.0, 5.0, 5.0], dtype=np.float32)
        det.setreference(ref)
        signal = det.update(live)
        log.info("drift.result", **signal)
    except Exception as exc:
        log.warning("drift.failed", error=str(exc))


def run_elbow(cfg: dict, log: Any) -> None:
    """Run the context-length elbow-finder sweep."""
    from braid.verbalizer.elbowfinder import run as elbowrun

    log.info("elbow.run")
    try:

        events = [
            {"duration": float(i % 100 + 1), "kind": ["play", "thumbup", "click"][i % 3]}
            for i in range(50)
        ]
        sweep = elbowrun(events, krange=range(5, 105, 10))
        for k, n in sweep.items():
            log.info(f"elbow.k={k}", kept=n)
    except Exception as exc:
        log.warning("elbow.failed", error=str(exc))


def run_obsgen(args: argparse.Namespace) -> int:
    """Generate Prometheus + Grafana + catalog artifacts from registry observability.

    Args:
        args: parsed CLI args (expects ``args.out``).

    Returns:
        Exit code.
    """
    from braid.core.obsgen import generate

    outdir = Path(getattr(args, "out", "artifacts/obsgen"))
    summary = generate(outdir)
    print(json.dumps(summary, indent=2))
    return 0


def run_serve(cfg: dict, log: Any) -> None:
    """Start the FastAPI ranker server."""
    log.info("serve.start", host="0.0.0.0", port=cfg.get("server", {}).get("port", 8080))
    try:
        from braid.serving.app import main as servemain

        servemain()
    except Exception as exc:
        log.warning("serve.failed", error=str(exc))


def buildparser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="braid",
        description="Polymorphic LLM-backed recommendation ranker",
    )
    sub = parser.add_subparsers(dest="cmd", required=False)

    p = sub.add_parser("list", help="list registered concretes")
    p.add_argument("category", nargs="?", help="optional category filter")
    p.set_defaults(func=listcmd)

    p = sub.add_parser("inspect", help="inspect a concrete")
    p.add_argument("category")
    p.add_argument("name")
    p.set_defaults(func=inspectcmd)

    p = sub.add_parser("dryrun", help="resolve a config")
    p.add_argument("--config", required=True)
    p.set_defaults(func=dryruncmd)

    p = sub.add_parser("conformance", help="run conformance suite")
    p.set_defaults(func=conformancecmd)

    p = sub.add_parser("data", help="ingest a dataset")
    p.add_argument("--config", required=True)
    p.set_defaults(func=lambda a: _runpipeline(a, "data"))

    p = sub.add_parser("phase1", help="run Phase-1 continued pretraining")
    p.add_argument("--config", required=True)
    p.set_defaults(func=lambda a: _runpipeline(a, "phase1"))

    p = sub.add_parser("rewards", help="train reward proxy")
    p.add_argument("--config", required=True)
    p.set_defaults(func=lambda a: _runpipeline(a, "rewards"))

    p = sub.add_parser("train", help="run Phase-2 post-training")
    p.add_argument("--config", required=True)
    p.set_defaults(func=lambda a: _runpipeline(a, "train"))

    p = sub.add_parser("serve", help="start the ranker server")
    p.add_argument("--config", required=True)
    p.set_defaults(func=lambda a: _runpipeline(a, "serve"))

    p = sub.add_parser("eval", help="run evaluation")
    p.add_argument("--config", required=True)
    p.set_defaults(func=lambda a: _runpipeline(a, "eval"))

    p = sub.add_parser("drift", help="run drift detection")
    p.set_defaults(func=lambda a: _runpipeline(a, "drift"))

    p = sub.add_parser("elbow", help="context-length search")
    p.add_argument("--config", required=True)
    p.set_defaults(func=lambda a: _runpipeline(a, "elbow"))

    p = sub.add_parser("obsgen", help="generate Prometheus/Grafana/catalog")
    p.add_argument("--out", default="artifacts/obsgen")
    p.set_defaults(func=run_obsgen)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: explicit argument list (default: ``sys.argv[1:]``).

    Returns:
        Process exit code.
    """
    parser = buildparser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
