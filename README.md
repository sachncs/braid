# braid

> Braiding signals into ranks. A polymorphic LLM-backed recommendation ranker.

`braid` is an end-to-end library for **verbalized, multi-reward, catalog-aware recommendation ranking** built on a polymorphic spine. Every primitive — backbones, catalog stores, verbalizers, rewards, losses, evaluators, monitoring — is registry-dispatched and configurable from a single Pydantic config.

[![CI](https://github.com/sachncs/braid/actions/workflows/ci.yml/badge.svg)](https://github.com/sachncs/braid/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

## Status

| | |
|---|---|
| **Categories** | 44 |
| **Real concretes** | 147 |
| **Conformance (real-pass)** | 131 / 147 |
| **Tests passing** | 277 passed + 1 skipped |
| **Lint** | ruff (E, F, W) clean |
| **Silent fallbacks** | none — typed `requiresenvironment` raised |

The numbers above are reproducible from the registry and the test
suite; regenerate any time with `make status` (see below) or
`pytest -q`.

## Single-word naming

Every identifier is **one lowercase word**. No snake_case, no camelCase, no underscore prefixes.

Examples:
- `phase/pretrain.py` (not `phase1_pretrain.py`)
- `indexer/hash.py` (not `hashindexer.py`)
- `miner/checkpoint.py` (not `checkpointtopkminer.py`)
- `quantizer/trainer.py` (not `rqvae_phase.py`)
- `braid/rqvae/` → `braid/quantizer/` (no opaque acronyms in dir names)

See `docs/decision_log.md` for the full rename mapping.

## Polymorphic spine

Three composites register like everything else:
- `braidedloss` (weighted sum of loss terms)
- `composite` (reward) — weighted sum of reward modules
- `composite` (eval) — merges evaluator reports

Eight layers on top of the registry:

1. **Registry** — `braid.registry.create(category, name, **cfg)`
2. **Traits** — `streamable`, `cachable`, `persistable`, `observable`, `idempotent`, `asyncable`, `distributable`, `teachable`
3. **Lifecycle** — `setup` / `warmup` / `shutdown` / `health` on every concrete
4. **Capabilities** — `gpu`, `async`, `fusedkernel`, `int4quantize`, `distributable`, `teachable`, etc.
5. **Versioning** — `configmigrator` walks configs between versions
6. **Schema** — versioned schemas (item, event, context, prompt, rankrequest/response)
7. **Observability** — concrete declares `observability()` and `metrics()`; `braid obsgen` walks the registry and emits Prometheus rules + Grafana JSON + a metric catalogue
8. **Context** — `requestcontext` flows through every layer

## Fail-fast

Missing dependencies or resources raise typed errors:
- `requiresenvironment` — package / driver unavailable (install hint included)
- `requiresresource` — model / data / file missing (HTTP hint included)
- `configurationerror` — malformed config
- `ioerror` — file/network problems

There are no silent fallbacks. The conformance suite (`make conformance`) reports `131/147` real-pass plus `16` skipped (concretes that could not be constructed in the offline sandbox). See `braid.core.conformance.verifyall()` for the live count.

## Concurrency target: CPU/MPS

Removed because they require Kubernetes / live network / commercial inference engines:
- `datasource:s3parquet`, `:kafka`, `:postgres`
- `datasink:postgres`
- `cflog:kafkacflog`, `:postgrescflog`
- `cache:redis`, `:memcached`
- `auth:oauth2`
- `secret:vault`, `:k8s`
- `tracing:otlp`, `:jaeger`
- `metrics:otelotlp`, `:statsd`
- `log:logfmt`
- `server:triton`, `:openaicompat`

Kept (CPU/MPS-runnable): 147 concretes across 44 categories.

## What this looks like in practice

```bash
$ python -m braid list
[auth] (3)
  apikey   caps: distributable,observable
  jwt      caps: distributable,observable
  none     caps: observable
[backbone] (4)
  llama32      caps: distributable,gpu,observable,teachable
  minicpm5     caps: distributable,gpu,observable,teachable
  pythia1      caps: distributable,gpu,observable,teachable
  qwen25       caps: distributable,gpu,observable,teachable
[batcher] (4)
  bucket   caps: observable
  padded   caps: observable
  packed   caps: observable
  sorted   caps: observable
... (44 categories, 147 concretes)

$ python -m braid inspect catalogstore matmulinmem
name       matmulinmem
category   catalogstore
version    1.0.0
module     braid.catalogstore.matmulinmem
capabilities   distributable,observable
methods:
  build
  metrics
  numshards
  observability
  score
  shardrank
  warmup

$ python -m braid dryrun --config configs/train/phase2.yaml
{
  "wouldinstantiate": [
    {"category": "backbone", "name": "minicpm5", "config": {"checkpoint": "..."}},
    {"category": "catalogstore", "name": "matmulinmem", "config": {}},
    ...
    {"category": "rewards", "name": "composite", "config": {"members": [...]}},
    {"category": "miner", "name": "checkpoint", "config": {"k": 64}}
  ]
}
```

The braided loss is a weighted sum of registered loss terms:
`Σ wᵢ · lossᵢ(scores, labels, …)` — see `braid/loss/braidedloss.py`.

## Quick start

```bash
make bootstrap                          # install deps + pre-commit hooks
make list                               # 44 categories × 147 concretes
make inspect CAT=backbone NAME=minicpm5
make dryrun CFG=configs/train/phase2.yaml
make conformance                        # 131/147 real-pass + 16 skipped
make test                               # 277 passed + 1 skipped
make obsgen                             # Prometheus + Grafana + catalogue
```

The CLI is the registry:

```bash
python -m braid list                                 # all categories
python -m braid inspect catalogstore matmulinmem    # one concrete
python -m braid dryrun --config configs/train/phase2.yaml
python -m braid conformance                          # full sweep
python -m braid eval     --config configs/train/phase2.yaml
python -m braid elbow    --config configs/train/phase2.yaml
python -m braid drift
python -m braid obsgen --out artifacts/obsgen        # Prometheus rules + Grafana
```

## Categories (44)

`auth (3)`, `backbone (4)`, `bandit (3)`, `batcher (4)`, `cache (1)`, `catalogstore (4)`, `cflog (1)`, `checkpoint (4)`, `curriculum (5)`, `datasink (2)`, `datasource (1)`, `drift (4)`, `driftresponse (3)`, `embedding (3)`, `eval (7)`, `indexer (4)`, `log (2)`, `loss (6)`, `metadata (3)`, `metrics (1)`, `migrator (1)`, `miner (5)`, `optimizer (4)`, `phase (5)`, `quantizer (5)`, `rankaggregator (3)`, `ratelimit (3)`, `regularizer (4)`, `reqpre (3)`, `resppost (3)`, `reward (5)`, `router (4)`, `scheduler (4)`, `secret (1)`, `server (2)`, `sessionizer (3)`, `splitter (3)`, `template (3)`, `tokencounter (3)`, `tokenizer (3)`, `tracing (1)`, `tracker (4)`, `truncation (5)`, `verbalizer (5)`.

## Tests

```bash
make test                     # full suite (all markers)
make conformance              # sweeps all 147 concretes
make integration              # registry / phase / loss / reward / e2e contracts
make e2e                      # CLI / pipeline smoke tests
```

## License

MIT
