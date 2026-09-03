#!/usr/bin/env bash
# Smoke test: training phase through CLI
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m braid dryrun --config configs/train/phase2.yaml
echo "---"
python3 -c "
import braid, yaml
cfg = yaml.safe_load(open('configs/train/phase2.yaml'))
phase_obj = braid.registry.create('phase', cfg['phase']['type'], maxsteps=cfg.get('maxsteps', 10))
print('training phase instantiated:', type(phase_obj).__name__)
print('  maxsteps:', phase_obj.maxsteps)
print('  braidterms:', phase_obj.braidterms)
"
