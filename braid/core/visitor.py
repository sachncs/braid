"""Visitor pattern for metric reports."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class metricvisitor(Protocol):
    """Walks a metric/report tree and emits an output.

    Implementations: ``htmlreporter``, ``jsonreporter``, ``csvreporter``, ``mdreporter``.
    """

    def visitreport(self, report: Any) -> Any: ...


class htmlreporter:
    """Render a report dict as an HTML fragment."""

    def visitreport(self, report: Any) -> str:
        rows: list[str] = []
        for section, metrics in report.items() if isinstance(report, dict) else []:
            rows.append(f"<h3>{section}</h3><table>")
            for name, value in metrics.items() if isinstance(metrics, dict) else []:
                rows.append(f"<tr><td>{name}</td><td>{value}</td></tr>")
            rows.append("</table>")
        return "<div>" + "\n".join(rows) + "</div>"


class jsonreporter:
    """Serialize a report dict to JSON."""

    def visitreport(self, report: Any) -> str:
        import json

        return json.dumps(report, indent=2, default=str)


class csvreporter:
    """Flatten a report dict to CSV."""

    def visitreport(self, report: Any) -> str:
        lines = ["section,metric,value"]
        if isinstance(report, dict):
            for section, metrics in report.items():
                if isinstance(metrics, dict):
                    for name, value in metrics.items():
                        lines.append(f"{section},{name},{value}")
        return "\n".join(lines)


class mdreporter:
    """Render a report dict as Markdown."""

    def visitreport(self, report: Any) -> str:
        lines: list[str] = []
        if isinstance(report, dict):
            for section, metrics in report.items():
                lines.append(f"## {section}\n")
                if isinstance(metrics, dict):
                    lines.append("| metric | value |\n|---|---|\n")
                    for name, value in metrics.items():
                        lines.append(f"| {name} | {value} |")
        return "\n".join(lines)
