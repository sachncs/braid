# braid architecture

> Braiding signals into ranks. A polymorphic LLM-backed recommendation ranker.

`braid` is a production library for building catalog-aware, multi-reward
recommendation rankers on top of large language models — patterned after the
Netflix GenRec paper (https://arxiv.org/html/2608.10257v2).

## The polymorphic spine

Every primitive in `braid` is registered under one of **43 categories** and
exchanged via a single dispatch API: `braid.registry.create(category, name, **cfg)`.

```
                    ┌─────────────────────────────────────────┐
                    │             Pydantic Cfg               │
                    └─────────────────────────────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────────┐
                    │      registry.create(category, name)    │
                    └─────────────────────────────────────────┘
                                       │
        ┌─────────────────┬───────────┴───────────┬──────────────────┐
        ▼                 ▼                       ▼                  ▼
   Backbone        CatalogStore            Verbalizer         RewardModel
        │                 │                       │                  │
        │                 │                       ▼                  │
        │                 │                Truncation               ▼
        │                 ▼                Template           Composite
        │           CatalogIndexer        Tokenizer            (registered reward)
        │                 │                       │
        │                 │                       ▼
        │                 │                TokenCounter
        │                 ▼
        │           EmbeddingBackend
        │
        ▼
   ScheduleFree/AdamW/Lion ── Optimizer/Scheduler/Checkpoint
        │
        ▼
   Miner/Curriculum/Regularizer ── Phase (phase1/rewardproxy/phase2/distillation/rqvae)
        │
        ▼
   Server/Vllm/Hflocal/Triton ── Cache/Auth/RateLimit/ReqPre/RespPost
        │
        ▼
   Eval (offline + replay + interleaving + composite) ── Drift/DriftResponse
        │
        ▼
   Metrics/Tracing/Log/Secret/Router/CfLog/Bandit/RankAggregator
```

Three composites sit on top:
- **`braidedloss`** — weighted sum of loss terms.
- **`compositereward`** — weighted sum of rewards.
- **`composite`** (eval) — merged reports across evaluators.

## Trait system

Concretes opt in to traits:

| Trait | Required methods |
|---|---|
| `streamable` | `openstream`, `read`, `aread`, `sessionize`, `split`, or `query` |
| `cachable` | `cacheget`, `cacheput`, `cacheinvalidate` |
| `persistable` | `persist`, `restore` |
| `idempotent` | `idempotencykey` |
| `distributable` | `shardrank`, `numshards` |
| `observable` | `observability`, `metrics` |

A concrete declares its traits via the `capabilities` class attribute
(frozenset). Trait enforcement is a soft check (warnings) at conformance time.

## Capability declaration

Every concrete declares a `capabilities: frozenset[str]` of things like
`gpu`, `async`, `fusedkernel`, `int4quantize`, `streamable`. The registry can
resolve by capability:

```python
braid.registry.findwithcap("int4quantize")
# → [("catalogstore", "matmulint4awq"), ...]
```

## Lifecycle

Every registered concrete, when constructed, gets a `lifecycledelegate` wrapper
providing uniform `setup`, `warmup`, `shutdown`, `health` hooks. Classes may
override these directly.

## Observability-as-Protocol

Concrete classes emit their observability surface via `observability()`. The
`obsgen` CLI walks the registry and emits Prometheus rules + Grafana panels:

```bash
make obsgen
# → grafana/dashboards/braid.json
# → grafana/alerts.yml
```

## Naming convention

- One lowercase word per identifier.
- No snake_case, no camelCase, no `_` prefixes.
- Convention intentionally deviates from PEP 8 (lowercase class names) per
  the project's single-word mandate.

## Directory layout

```
braid/
  core/      # registry, traits, lifecycle, capability, versioning, schema,
             # observability, context, transform, serialize, visitor,
             # conformance, error, cli
  testing/   # scaledown, fixtures, contracts, tinytokenizer
  data/      # datasource, datasink, sessionizer, splitter, metadata, ingest,
             # schemas
  verbalizer/  # truncation, template, tokenizer, tokencounter, 5 verbalizers
  backbone/  # minicpm5, llama32, qwen25, pythia1
  rewards/   # longtermreturn, diversitybonus, contenttypebalance, noveltyreward,
             # composite
  catalogstore/  # matmulinmem, matmulint4awq, faissivfstore, rqvaestore
  indexer/   # hash, exact, faiss, hnsw
  embedding/ # safetensors, onnx, torchscript
  loss/      # rankingce, lmax, rewardweighted, diversityentropy, calibration,
             # braidedloss
  optimizer/ # adamw, lion, adafactor, schedulefree
  scheduler/ # cosine, linearwarmupcosine, wsd, constant
  checkpoint/  # best, latest, everyn, ema
  regularizer/  # dropout, labelsmoothing, mixup, tokendropout
  tracker/   # aim, mlflow, wandb, tensorboard
  phase/     # phase1pretrain, rewardproxyphase, rqvaephase, phase2postrain,
             # distillationphase
  miner/     # random, inbatch, checkpointtopk, popularityaware, contrastive
  curriculum/ # linear, cosine, step, adaptive, twostage
  batcher/   # padded, packed, lengthbucketed, sortedpadded
  server/    # vllm, triton, hflocal, openaicompat
  cache/     # lru, redis, memcached
  auth/      # apikey, jwt, oauth2, noauth
  ratelimit/ # tokenbucket, slidingwindow, leakybucket
  reqpre/    # normalize, validate, redactpii
  resppost/  # rerank, diversity, calibrate
  eval/      # offlineranking, calibration, diversity, replay, interleaving,
             # baseline, composite
  metrics/   # prometheus, otelotlp, statsd
  drift/     # psi, ks, jsd, pagehinkley
  driftresponse/  # alert, retraintrigger, fallbackbaseline
  tracing/   # otlp, jaeger, console
  log/       # structlogjson, logfmt, plain
  secret/    # env, vault, k8s
  router/    # random, stickybucket, contextualbandit, shadow
  cflog/     # parquet, kafka, postgres
  bandit/    # epsilongreedy, linucb, thompson
  rankaggregator/  # borda, rrf, condorcet
  rqvae/     # residualquantizer, encoder, decoder, index, catalogstore,
             # phase
  serving/   # FastAPI app, prefill, scoring, prefixcache, lifecycle
  training/  # loop, data_module, grad_accum, mixed_precision
  obsgen.py  # obsgen CLI: emits Prometheus rules + Grafana dashboards
```

## CLI

```
braid list                                  # all categories + concretes + capabilities
braid list <category>                       # one category
braid inspect <category> <name>             # single concrete: name/version/caps/methods
braid dryrun --config <yaml>                # resolve config without executing
braid data     --config configs/data/movielens.yaml
braid phase1   --config configs/phase1/pretrain.yaml
braid rewards  --config configs/rewards/proxy.yaml
braid train    --config configs/train/phase2.yaml
braid serve    --config configs/serve/vllm.yaml
braid eval     --config configs/train/phase2.yaml
braid drift
braid elbow    --config configs/train/phase2.yaml
python -m braid.obsgen --output grafana/     # emit dashboards + alerts
```

## Conformance

```bash
make conformance
```

Sweeps every concrete across every category through the polymorphic
conformance harness. Construction failures are skipped (passed=True). Trait
mismatches are surfaced as warnings. Observability is required.
