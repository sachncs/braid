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
    _flatten(raw, flat)
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


def _flatten(node: Any, out: dict[str, Any], prefix: str = "") -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                if "type" in v:
                    out[path] = v
                else:
                    _flatten(v, out, path)
            else:
                out[path] = v


def conformancecmd(args: argparse.Namespace) -> int:
    """Run the conformance suite.

    Args:
        args: parsed CLI args.

    Returns:
        Exit code (0 if all pass).
    """
    from braid.core.conformance import verifyall

    results = verifyall()
    failed = [r for r in results if not r.passed]
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"{status}  {r.category}.{r.name}")
        for f in r.failures:
            print(f"       {f}")
    print(f"\n{len(results) - len(failed)}/{len(results)} passed")
    return 0 if not failed else 1


def _runpipeline(args: argparse.Namespace, phase: str) -> int:
    """Dispatch a phase subcommand by constructing the registered concrete.

    Args:
        args: parsed CLI args.
        phase: pipeline name (``data``, ``phase1``, ``rewards``, ``train``,
            ``serve``, ``eval``, ``drift``, ``elbow``).

    Returns:
        Exit code.
    """
    from braid.core.error import configurationerror

    cfg_path = getattr(args, "config", None)
    if not cfg_path:
        print(f"error: --config is required for {phase}", file=sys.stderr)
        return 2
    cfg_raw = yaml.safe_load(Path(cfg_path).read_text())
    log = __import__("importlib").import_module("braid.core.logging").getlogger(f"braid.cli.{phase}")
    log.info("pipeline.start", phase=phase, config=cfg_path)

    if phase == "data":
        run_data(cfg_raw, log)
    elif phase == "phase1":
        run_phase(cfg_raw, "pretrain", log)
    elif phase == "rewards":
        run_phase(cfg_raw, "reward", log)
    elif phase == "train":
        run_postrain(cfg_raw, log)
    elif phase == "eval":
        run_eval(cfg_raw, log)
    elif phase == "drift":
        run_drift(cfg_raw, log)
    elif phase == "elbow":
        run_elbow(cfg_raw, log)
    elif phase == "serve":
        run_serve(cfg_raw, log)
    else:
        raise configurationerror(f"unknown pipeline: {phase}")
    log.info("pipeline.complete", phase=phase)
    return 0


def run_data(cfg: dict, log: Any) -> None:
    """Real data ingest pipeline (stub runner; concrete impl in R2)."""
    log.warning("ingest.runner_not_implemented", path=cfg.get("datasource", {}).get("path"))


def run_phase(cfg: dict, name: str, log: Any) -> None:
    """Construct and dispatch a phase concrete (pretrain/reward)."""
    log.info("phase.run", name=name, steps=cfg.get("maxsteps"))


def run_postrain(cfg: dict, log: Any) -> None:
    """Postrain pipeline (stub)."""
    log.info("postrain.run", braidterms=(cfg.get("loss") or {}).get("terms"))


def run_eval(cfg: dict, log: Any) -> None:
    """Eval pipeline (stub)."""
    log.info("eval.run")


def run_drift(cfg: dict, log: Any) -> None:
    """Drift detection pipeline (stub)."""
    log.info("drift.run")


def run_elbow(cfg: dict, log: Any) -> None:
    """Elbow-finder pipeline (stub)."""
    log.info("elbow.run")


def run_serve(cfg: dict, log: Any) -> None:
    """Serve pipeline (stub)."""
    log.info("serve.run", host="0.0.0.0", port=cfg.get("server", {}).get("port", 8080))


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
