"""Generate Prometheus alert rules, Grafana panels, and a metric catalogue.

The catalogue is built by walking the registry, calling ``observability()`` on
each concrete and pulling ``metrics()``. The output::

    * Prometheus rules YAML — ``artifacts/obsgen/prometheus.yml``
    * Grafana dashboard JSON — ``artifacts/obsgen/grafana.json``
    * Metric catalogue JSON — ``artifacts/obsgen/catalog.json``

All three are deterministic — sorting, no timestamps.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from braid.core.registry import registry


def _knownmetricdecls() -> list[dict[str, Any]]:
    """Walk every registered concrete and return its declared metric names."""
    rows: list[dict[str, Any]] = []
    for cat in registry.categories():
        for name in registry.available(cat):
            try:
                cls = registry.resolve(cat, name)
            except Exception:
                continue
            spec: dict[str, Any] = {}
            metrics: list[Any] = []
            try:
                # observability() is an instance method; try with a default instance.
                try:
                    inst = cls.__new__(cls)
                    spec = inst.observability() or {}
                except Exception:
                    spec = getattr(cls, "observability_static", lambda: {})()
            except Exception:
                spec = {}
            try:
                try:
                    inst = cls.__new__(cls)
                    metrics = inst.metrics() or []
                except Exception:
                    metrics = []
            except Exception:
                metrics = []
            for m in spec.get("metrics") or []:
                mtype = m.get("type", "gauge") if isinstance(m, dict) else "gauge"
                mname = m.get("name") if isinstance(m, dict) else getattr(m, "name", str(m))
                rows.append({"category": cat, "concrete": name, "metric": mname, "type": mtype})
            for m in metrics:
                rows.append({"category": cat, "concrete": name, "metric": str(m), "type": "gauge"})
    rows.sort(key=lambda r: (r["metric"], r["category"], r["concrete"]))
    return rows


def _aggregatorules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Derive Prometheus alert rules from the metric list.

    Heuristics:
        * name contains ``error`` → ``> 0`` for 1m
        * name contains ``drift`` → ``> 0.2`` for 5m
        * name contains ``lag`` → ``> 5`` for 1m
        * else → ``< 0`` for 1m (gauge sanity)
    """
    rules: dict[str, dict[str, Any]] = defaultdict(lambda: {"expr": "", "for": "1m", "summary": "", "severity": "warning"})
    by_metric: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_metric[r["metric"]].append(r)
    for metric, examples in by_metric.items():
        rule = rules[metric]
        m = metric.lower()
        if "error" in m:
            rule["expr"] = f"sum(rate({metric}{{category!=\"\"}}[1m])) > 0"
            rule["severity"] = "critical"
        elif "drift" in m:
            rule["expr"] = f"avg_over_time({metric}{{category!=\"\"}}[5m]) > 0.2"
            rule["severity"] = "warning"
        elif "lag" in m:
            rule["expr"] = f"avg_over_time({metric}{{category!=\"\"}}[1m]) > 5"
            rule["severity"] = "warning"
        else:
            rule["expr"] = f"avg_over_time({metric}{{category!=\"\"}}[1m]) < 0"
            rule["severity"] = "info"
        rule["summary"] = f"alert on {metric} (declared by {len(examples)} concretes)"
    return [dict(name=k, **v) for k, v in sorted(rules.items())]


def _panelfor(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a Grafana dashboard JSON embedding every metric as a stat panel."""
    panels: list[dict[str, Any]] = []
    for i, r in enumerate(rows):
        panels.append(
            {
                "id": i + 1,
                "type": "stat",
                "title": r["metric"],
                "datasource": "Prometheus",
                "targets": [
                    {
                        "expr": r["metric"],
                        "legendFormat": "{{category}}.{{concrete}}",
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "unit": "short",
                        "thresholds": {"mode": "absolute", "steps": [{"color": "green"}, {"color": "red", "value": 0.5}]},
                    }
                },
                "gridPos": {"h": 4, "w": 6, "x": (i % 4) * 6, "y": (i // 4) * 4},
            }
        )
    return {
        "title": "braid — registry-wide observability",
        "uid": "braid-registry",
        "schemaVersion": 39,
        "panels": panels,
        "tags": ["braid"],
    }


def generate(out: str | Path = "artifacts/obsgen") -> dict[str, Any]:
    """Generate observability artifacts.

    Args:
        out: directory to write into.

    Returns:
        A summary dict with counts of metrics/rules/panels.
    """
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = _knownmetricdecls()
    rules = _aggregatorules(rows)
    dashboard = _panelfor(rows)
    catalog = {"metrics": rows, "count": len(rows)}
    (out / "prometheus.yml").write_text(
        "groups:\n  - name: braid\n    rules:\n"
        + "".join(
            f"      - alert: {r['name']}\n        expr: {r['expr']}\n        for: {r['for']}\n        labels:\n          severity: {r['severity']}\n        annotations:\n          summary: '{r['summary']}'\n"
            for r in rules
        )
    )
    (out / "grafana.json").write_text(json.dumps(dashboard, indent=2))
    (out / "catalog.json").write_text(json.dumps(catalog, indent=2))
    return {"metrics": len(rows), "rules": len(rules), "panels": len(dashboard["panels"])}
