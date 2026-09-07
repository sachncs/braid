#!/usr/bin/env bash
# Run all tests
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m pytest tests/ -q 2>&1 | tail -10
