#!/usr/bin/env python3
"""Print a single-source-of-truth status block for braid.

Used by the README and the audit sweep. Run with ``python scripts/status.py``.
"""

from __future__ import annotations

import subprocess

import braid
from braid.core.conformance import verifyall


def main() -> int:
    cats = braid.registry.categories()
    concretes = sum(len(braid.registry.available(c)) for c in cats)
    results = verifyall()
    realpass = sum(1 for r in results if r.passed)
    skipped = sum(1 for r in results if r.skipped)
    try:
        out = subprocess.run(
            ["pytest", "tests/"],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        lines = reversed(out.stdout.splitlines())
        summary = next(
            (line for line in lines if "passed" in line or "failed" in line),
            "(no summary)",
        )
        last = summary.strip()
    except Exception as exc:
        last = f"(pytest unavailable: {exc})"
    print("braid status")
    print("============")
    print(f"Categories          : {len(cats)}")
    print(f"Real concretes      : {concretes}")
    print(f"Conformance         : {realpass}/{len(results) - skipped} real-pass, {skipped} skipped")
    print(f"Tests               : {last}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
