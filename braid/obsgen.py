"""Generate Prometheus rules and Grafana dashboards from declared observability.

Walks the registry, asks each concrete for its ``observability()``, and emits:
- ``grafana/dashboards/braid.json`` — a unified dashboard.
- ``prometheus/alerts.yml`` — recommended alerts per metric.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from braid.core.registry import registry


def collect() -> list[dict]:
    """Walk the registry and collect declared observability.

    Returns:
        A list of ``{category, name, capabilities, metrics, traces, logs}``.
    """
    out: list[dict] = []
    for category, name in [
        (c, n)
        for c in registry.categories()
        for n in registry.available(c)
    ]:
        try:
            obj = registry.create(category, name)
            obs = obj.observability() if hasattr(obj, "observability") else {}
        except Exception:  # noqa: BLE001
            continue
        entry = {
            "category": category,
            "name": name,
            "capabilities": sorted(getattr(obj, "capabilities", frozenset())),
            "metrics": obs.get("metrics", []) if isinstance(obs, dict) else [],
            "traces": obs.get("traces", []) if isinstance(obs, dict) else [],
            "logs": obs.get("logs", []) if isinstance(obs, dict) else [],
        }
        out.append(entry)
    return out


def renderdashboard(entries: list[dict]) -> dict:
    """Render a Grafana dashboard JSON from observations."""
    panels: list[dict] = []
    for i, e in enumerate(entries):
        for m in e["metrics"]:
            panels.append(
                {
                    "title": f"{e['category']}.{e['name']}.{m.get('name', 'm')}",
                    "type": "timeseries",
                    "targets": [{"expr": m.get("name", "")}],
                    "gridPos": {"h": 8, "w": 12, "x": (i * 12) % 24, "y": 0},
                }
            )
    return {
        "title": "braid ranker observability",
        "panels": panels,
        "schemaVersion": 39,
        "version": 1,
        "refresh": "30s",
    }


def renderalerts(entries: list[dict]) -> str:
    """Render Prometheus alert rules."""
    lines = ["groups:"]
    lines.append("  - name: braid")
    lines.append("    rules:")
    for e in entries:
        for m in e["metrics"]:
            name = m.get("name", "")
            if not name:
                continue
            lines.append(f"      - alert: braid_{name.replace('.', '_')}_p95_high")
            lines.append(f"        expr: histogram_quantile(0.95, sum(rate({name}[5m])) by (le)) > 200")
            lines.append(f"        for: 5m")
            lines.append(f"        labels:")
            lines.append(f"          severity: warning")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: explicit args (default: ``sys.argv[1:]``).

    Returns:
        Process exit code.
    """
    parser = argparse.ArgumentParser(description="Generate observability assets.")
    parser.add_argument("--output", default="grafana/")
    args = parser.parse_args(argv)

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    entries = collect()
    dashboard = renderdashboard(entries)
    alerts = renderalerts(entries)

    (out / "dashboards" / "braid.json").parent.mkdir(parents=True, exist_ok=True)
    (out / "dashboards" / "braid.json").write_text(json.dumps(dashboard, indent=2))
    (out / "alerts.yml").write_text(alerts)
    print(f"wrote {len(entries)} observability specs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
