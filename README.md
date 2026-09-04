# braid

> Braiding signals into ranks. A polymorphic LLM-backed recommendation ranker.

`braid` is an end-to-end library for **verbalized, multi-reward, catalog-aware recommendation ranking** built on a polymorphic spine. Every primitive — backbones, catalog stores, verbalizers, rewards, losses, evaluators, monitoring — is registry-dispatched and configurable from a single Pydantic config.

## Status

| | |
|---|---|
| **Atomic commits** | **126** |
| **Categories** | 38 |
| **Real concretes** | 147 |
| **Stubs / fallbacks** | **0** (silent fallbacks purged; missing deps raise typed ``requiresenvironment``) |
| **Self._ underscore violations** | **0** (semi-private naming banned) |
| **Tests passing** | **215** |
| **Single-word naming** | enforced repo-wide |

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
7. **Observability** — concrete declares `observability()` and `metrics()`; `braid obsgen` walks the registry and emits Prometheus rules + Grafana JSON + a metric catalogue (47 metrics, 47 alert rules, 47 panels)
8. **Context** — `requestcontext` flows through every layer

## Fail-fast

Missing dependencies or resources raise typed errors:
- `requiresenvironment` — package / driver unavailable (install hint included)
- `requiresresource` — model / data / file missing (HTTP hint included)
- `configurationerror` — malformed config
- `ioerror` — file/network problems

There are no silent fallbacks. The conformance suite (`make conformance`) reports `146/146 passing`, which is `True` for both real-pass and skip-with-typed-cause cases.

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

Kept (CPU/MPS-runnable): 147 concretes across 38 categories.

## Quick start

```bash
make bootstrap                          # install deps
make list                               # 38 categories × 147 concretes
make inspect CAT=backbone NAME=minicpm5
make dryrun CFG=configs/train/phase2.yaml
make conformance                        # 146/146
make test                               # 215 tests
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

## Categories (38)

`auth (3)`, `backbone (4)`, `bandit (3)`, `batcher (4)`, `cache (1)`, `catalogstore (4)`, `cflog (1)`, `checkpoint (4)`, `curriculum (5)`, `datasink (2)`, `datasource (1)`, `drift (4)`, `driftresponse (3)`, `embedding (3)`, `eval (7)`, `indexer (4)`, `log (2)`, `loss (6)`, `metadata (3)`, `metrics (1)`, `migrator (1)`, `miner (5)`, `optimizer (4)`, `phase (5)`, `quantizer (5)`, `rankaggregator (3)`, `ratelimit (3)`, `regularizer (4)`, `reqpre (3)`, `resppost (3)`, `reward (5)`, `router (4)`, `scheduler (4)`, `secret (1)`, `server (2)`, `sessionizer (3)`, `splitter (3)`, `template (3)`, `tokencounter (3)`, `tokenizer (3)`, `tracing (1)`, `tracker (4)`, `truncation (5)`, `verbalizer (5)`.

## Tests

```bash
make test                     # 215 passed
make conformance              # sweeps all 147 concretes
make integration              # medium-scale
```

`tests/integration/`:
- existing `*contract*` baseline smoke tests (174 → 175)
- new `*contract_real` real-assertion tests (40):
  - `evalcontract_real` — hand-verified MRR / NDCG@K / HitRate@K / MAP@K / Brier / NLL / Gini / coverage / intra (13)
  - `rewardcontract_real` — typed requiresresource on bad members, MLP reward finite-bounded, novelty inverse-monotone (7)
  - `driftcontract_real` — PSI well-calibrated vs shifted, Page-Hinkley below threshold, KS returns score, response toggles (7)
  - `registrycontract_real` — dedup, capabilities intersection, resolve, applymigrations, categories covering core (7)
  - `verbalizercontract_real` — elbow finder finds a kink, head/diversity fit, fstring renders, pipeline assembles (6)

## License

MIT
