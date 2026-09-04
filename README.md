# braid

> Braiding signals into ranks. A polymorphic LLM-backed recommendation ranker.

`braid` is an end-to-end library for **verbalized, multi-reward, catalog-aware recommendation ranking** built on a polymorphic spine. Every primitive — backbones, catalog stores, verbalizers, rewards, losses, evaluators, monitoring — is registry-dispatched and configurable from a single Pydantic config.

## Status

| | |
|---|---|
| **Atomic commits** | 106 |
| **Categories** | 38 |
| **Real concretes** | 146 |
| **Stubs / fallbacks** | **0** (silent fallbacks purged; missing deps raise typed ``requiresenvironment``) |
| **Tests passing** | 174 |

## Single-word naming

Every identifier is **one lowercase word**. No snake_case, no camelCase, no underscore prefixes.

Examples:
- `phase/pretrain.py` (not `phase1_pretrain.py`)
- `indexer/hash.py` (not `hashindexer.py`)
- `miner/checkpoint.py` (not `checkpointtopkminer.py`)
- `quantizer/trainer.py` (not `rqvae_phase.py`)
- `braid/rqvae/` → `braid/quantizer/` (no opaque acronyms in dir names)

Fail-fast when violated: `make lint`.

## Polymorphic spine

Eight layers on top of the registry:

1. **Registry** — `braid.registry.create(category, name, **cfg)`
2. **Traits** — `streamable`, `cachable`, `persistable`, `observable`, `idempotent`, `asyncable`, `distributable`, `teachable`
3. **Lifecycle** — `setup` / `warmup` / `shutdown` / `health` on every concrete
4. **Capabilities** — `gpu`, `async`, `fusedkernel`, `int4quantize`, `distributable`, `teachable`, etc.
5. **Versioning** — `configmigrator` walks configs between versions
6. **Schema** — versioned schemas (item v1/v2, event v1/v2, context, prompt, rankrequest/response)
7. **Observability** — concrete declares `metricdecl`/`tracedecl`/`logdecl`
8. **Context** — `requestcontext` flows through every layer

Three composites register like everything else:
- `braidedloss` (weighted sum of loss terms)
- `compositereward` (weighted sum of reward modules)
- `composite` (eval) — merges evaluator reports

## Concurrency target: CPU/MPS

Removed because they can't run here:
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

Kept (CPU/MPS-runnable): 146 concretes across 38 categories.

## Quick start

```bash
make bootstrap
make list                  # 38 categories, 146 concretes
make inspect CAT=backbone NAME=minicpm5
make dryrun CFG=configs/train/phase2.yaml
make conformance
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
```

## Categories (38)

`auth (3)`, `backbone (4)`, `bandit (3)`, `batcher (4)`, `cache (1)`, `catalogstore (4)`, `cflog (1)`, `checkpoint (4)`, `curriculum (5)`, `datasink (2)`, `datasource (1)`, `drift (4)`, `driftresponse (3)`, `embedding (3)`, `eval (7)`, `indexer (4)`, `log (2)`, `loss (6)`, `metadata (3)`, `metrics (1)`, `migrator (1)`, `miner (5)`, `optimizer (4)`, `phase (5)`, `quantizer (5)`, `rankaggregator (3)`, `ratelimit (3)`, `regularizer (4)`, `reqpre (3)`, `resppost (3)`, `reward (4)`, `router (4)`, `scheduler (4)`, `secret (1)`, `server (2)`, `sessionizer (3)`, `splitter (3)`, `template (3)`, `tokencounter (3)`, `tokenizer (3)`, `tracing (1)`, `tracker (4)`, `truncation (5)`, `verbalizer (5)`.

## Tests

```bash
make test                     # 174 passed
make conformance              # sweeps all 146 concretes
make integration              # medium-scale
```

`tests/integration/` asserts real behavior (numpy-only, no torch dependency for fast checks). `tests/conformance/` sweeps every concrete through the polymorphic harness — verified working or skipped with a typed error.

## License

MIT
