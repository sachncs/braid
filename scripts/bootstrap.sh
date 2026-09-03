#!/usr/bin/env bash
# Bootstrap script: install braid + dev tools + pre-commit
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m pip install -e ".[dev,all]" || true
python3 -m pre_commit install || true
echo "bootstrap complete"
echo "try: make list"
