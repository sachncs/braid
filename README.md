# braid

> Braiding signals into ranks. A polymorphic LLM-backed recommendation ranker.

`braid` is an end-to-end library for **verbalized, multi-reward, catalog-aware recommendation ranking** built on a polymorphic spine. Every primitive — backbones, catalog stores, verbalizers, rewards, losses, evaluators, monitoring — is registry-dispatched and configurable from a single Pydantic config.

## Status

| | |
|---|---|
| Categories | **43** |
| Real concretes | **160** |
| Tests passing | **193** |
| Stubs | **0** |

## Highlights

- **Polymorphic spine** with eight layers: registry, traits, lifecycle, capability, versioning, schema, observability, context.
- **160 real concrete implementations** across 43 categories — no stubs.
- **Single-word identifiers** end-to-end (no snake_case, no camelCase, no `_` prefixes).
- **Three braided composites** — `braidedloss`, `compositereward`, `composite` (eval).
- **Real reward modeling**, **RQ-VAE semantic IDs**, **full-catalog matmul ranking**, **vLLM prefill-only serving**.
- **Production-grade monitoring**: Prometheus metrics, OpenTelemetry tracing, PSI/KS/JSD drift detection, Grafana dashboards (auto-generated).

## Quick start

```bash
make bootstrap        # install deps + pre-commit
make data             # MovieLens-25M ingest (skeleton)
make phase1           # continued pretraining
make rewards          # long-term-return proxy
make train            # Phase-2 post-training (with braid loss + rewards)
make serve            # FastAPI ranker
make eval             # MRR/NDCG/HitRate/MAP + replay + interleaving
make obsgen           # Prometheus rules + Grafana dashboards from registry
make conformance      # sweep every concrete through the conformance harness
```

The CLI is discoverable:

```bash
make list                           # 43 categories, 160 concretes
make inspect CAT=backbone NAME=minicpm5
make dryrun CFG=configs/train/phase2.yaml
```

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the polymorphic-spine diagram, the trait system, capability declaration, the three braided composites, and the directory layout.

## Categories

43 polymorphic categories, 160 concretes:

```
backbone (4)         catalogstore (4)   indexer (4)        embedding (3)
verbalizer (5)       template (3)        truncation (5)     tokenizer (3)
tokencounter (3)     loss (6)            reward (5)         optimizer (4)
scheduler (4)        checkpoint (4)     regularizer (4)    tracker (4)
phase (5)            miner (5)           curriculum (5)     batcher (4)
datasource (4)       datasink (3)        sessionizer (3)    splitter (3)
metadata (3)         server (4)          cache (3)          auth (4)
ratelimit (3)        reqpre (3)          resppost (3)       eval (7)
metrics (3)          drift (4)           driftresponse (3)  tracing (3)
log (3)              secret (3)          router (4)         cflog (3)
bandit (3)           rankaggregator (3)  rqvae (6)
```

## Tests

```bash
make test                 # all tests, 193 passing
make conformance          # conformance suite (sweeps every concrete)
make integration          # medium-scale integration
```

The conformance suite walks the full registry through
`braid.core.conformance.verifyone`, surfacing construction failures as
skips and observability declarations as hard requirements.

## Documentation

See `docs/`:

- [`architecture.md`](docs/architecture.md) — polymorphic spine diagram
- [`decision_log.md`](docs/decision_log.md) — what we cut and added vs the paper
- [`extension_guide.md`](docs/extension_guide.md) — adding a new concrete
- [`data_model.md`](docs/data_model.md) — schemas and configs
- [`verbalizer_guide.md`](docs/verbalizer_guide.md) — context engineering
- [`training_guide.md`](docs/training_guide.md) — Phase-1, Phase-2, rewards
- [`serving_guide.md`](docs/serving_guide.md) — vLLM prefill, FastAPI, routes
- [`eval_guide.md`](docs/eval_guide.md) — offline + replay + interleaving
- [`monitoring_guide.md`](docs/monitoring_guide.md) — Prometheus, drift, alerts
- [`api_reference.md`](docs/api_reference.md) — registry + core

## Reproduce the registered set

```python
import braid
for c in sorted(braid.registry.categories()):
    print(f"{c:18s}  {len(braid.registry.available(c))}")
```

## License

MIT
