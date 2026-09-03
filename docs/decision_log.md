# Decision log

## What we cut from the paper

### Multi-replica serving + load balancer
Out of scope for v1. Single replica. LB is a one-line gunicorn-style swap.

### Online RL (GRPO)
The GenRec paper explicitly calls online RL future work. We use
**reward-weighted CE** as the alignment mechanism in Phase-2. A real
RL head could be added by registering a `loss:grpo` concrete.

### Multi-content-type mixing logic
The Netflix catalog includes movies, shows, games, live, podcasts. Our
MovieLens target is movies-only — so we collapse business rebalancing to
**genre reweighting** via the `contenttypebalance` reward.

### Phase-1 continued pretraining from scratch
We do run Phase-1, but with the stock MiniCPM5-1B as the base. We do not
train an entirely new Phase-1 foundation model (compute budget).

## What we add beyond the paper

### Polymorphic spine
The paper focuses on the ranker. `braid` reframes the entire stack as a
registry of polymorphic categories with capability-and-trait contracts.

### Three braided composites
- `braidedloss` — weighted sum of loss terms.
- `compositereward` — composite over a multi-objective reward.
- `composite` (eval) — merge metrics across evaluators.

These are themselves registered concretes — composable via the same
mechanism as everything else.

### Observability-as-Protocol
Every concrete declares its observability surface via `observability()`. The
`obsgen` CLI generates Prometheus alert rules + Grafana panels from the
registry — no manual dashboard maintenance.

### Single-word naming convention
Every identifier is one lowercase word. No `_`, no camelCase. Convention
takes precedence over PEP 8.

### Real reward model
The paper's "reward modeling" is implied via context. We trained a
genuine MLP proxy for `longtermreturn` (predicts 30-day return from a
single engagement event). Real reward model, real versioning.

### Hard-negative mining
The paper uses in-batch. We register `random`, `inbatch`, `checkpointtopk`,
`popularityaware`, `contrastive` and let curriculum + reward shape the
training trajectory.

### Counterfactual logging
Every online request can log its full top-K to Parquet/Kafka/Postgres
without affecting responses. Enables offline replay and team-draft
interleaving at scale.

### Online bandit explorer
A/B routing and serving-time exploration are first-class via
`router` and `bandit` categories. `contextualbanditrouter` is a LinUCB
controller.

### Real rewards vs proxy aggregations
We don't approximate "diversity" as a heuristic. We train a proxy model
for `longtermreturn` and combine it with `diversitybonus` via `compositereward`.

## What we don't bother with (yet)

### KV-cache prefix reuse across replicas
Real distributed serving would shard this. Out of scope; `prefixcache` is
in-process.

### Quantization-aware training
The `matmulint4awq` store ingests prequantized embeddings. Quantization
happens offline; we don't expose QAT knobs.

### On-GPU calibration
The `resppost:calibrate` uses CPU-side temperature scaling. A GPU-side
variant can replace it via a `calibrategpu` concrete.

### Auto-rebuild on drift
The `driftresponse:retraintrigger` writes a trigger file. The actual
retraining pipeline is launched manually (or by an external orchestrator).
