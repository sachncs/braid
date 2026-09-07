# Decision Log

## Why a polymorphic registry?

`braid` is a recommendation ranker that has to support a wide range of backbones
(MiniCPM, Llama, Qwen, Pythia), catalog stores (numpy matmul, int4 awq, faiss IVF),
verbalizers (compact-elbow, narrative, structured JSON), rewards (long-term return,
diversity bonus, content-type balance, novelty, composite), losses (ranking-CE,
L-max, calibration, braided), evaluators (offline ranking, calibration, diversity,
replay, interleaving, baseline, composite), routers (random, sticky-bucket,
contextual bandit, shadow), drift detectors, monitoring, etc.

A polymorphic registry makes the entire surface area pluggable from a single config
file. Every CLI subcommand resolves to a registered concrete; every config field is
declared through the same `(category, name)` lookup. New research ideas drop in
without forking the training loop.

## Naming: one word, no separators

User constraint: every identifier (file name, class name, attribute) is **a single
lowercase word**. No snake_case, no camelCase, no underscore prefixes. Directories
provide all the context.

| Old (rejected)              | New (kept)                |
| --------------------------- | ------------------------- |
| `phase1_pretrain.py`        | `phase/pretrain.py`       |
| `phase2_postrain.py`        | `phase/postrain.py`       |
| `phase/reward_proxy_phase.py` | `phase/reward.py`        |
| `phase/rqvae_phase.py`      | `phase/codebook.py`       |
| `phase/distillation_phase.py` | `phase/distill.py`      |
| `indexer/hash_indexer.py`   | `indexer/hash.py`         |
| `indexer/exact_indexer.py`  | `indexer/exact.py`        |
| `indexer/faiss_indexer.py`  | `indexer/faiss.py`        |
| `indexer/hnsw_indexer.py`   | `indexer/hnsw.py`         |
| `rqvae/residual_quantizer.py` | `quantizer/quantizer.py` |
| `rqvae/codebook_index.py`   | `quantizer/semanticindex.py` |
| `rqvae/trainer.py`          | `quantizer/trainer.py`    |
| `rqvae/`                    | `quantizer/`              |
| `eval/diversity.py` (`diversityeval`) | `eval/diversity.py` (`diversity`) |
| `eval/replay.py` (`replayeval`)        | `eval/replay.py` (`replay`)        |
| `eval/interleaving.py` (`interleavingeval`) | `eval/interleaving.py` (`interleaving`) |
| `miner/checkpoint_topk_miner.py` | `miner/checkpoint.py`       |
| `miner/popularity_aware_miner.py` | `miner/popularity.py`       |
| `miner/contrastive_miner.py` | `miner/contrastive.py`      |
| `miner/in_batch_miner.py`   | `miner/inbatch.py`         |
| `miner/random_miner.py`     | `miner/random.py`          |
| `curriculum/linear_curriculum.py` | `curriculum/linear.py`     |
| `curriculum/cosine_curriculum.py` | `curriculum/cosine.py`     |
| `curriculum/adaptive_curriculum.py` | `curriculum/adaptive.py` |
| `curriculum/two_stage_curriculum.py` | `curriculum/twostage.py` |
| `batcher/padded_batcher.py` | `batcher/padded.py`        |
| `batcher/packed_batcher.py` | `batcher/packed.py`        |
| `batcher/length_bucketed_batcher.py` | `batcher/bucket.py`  |
| `batcher/sorted_padded_batcher.py` | `batcher/sorted.py`     |
| `driftresponse/fallback_baseline.py` | `driftresponse/fallback.py` |

The semi-private convention (`self._foo`) is also banned across the codebase.

## Trim (J-section)

Concurrent development of 146 concretes is sufficient. Removed from the registry:
`datasource:s3parquet`, `:kafka`, `:postgres`; `datasink:postgres`;
`cflog:kafkacflog`, `:postgrescflog`; `cache:redis`, `:memcached`; `auth:oauth2`;
`secret:vault`, `:k8s`; `tracing:otlp`, `:jaeger`; `metrics:otelotlp`, `:statsd`;
`log:logfmt`; `server:triton`, `:openaicompat`. These required network access,
Kubernetes, or a separately-licensed inference engine unavailable in the
offline sandbox.

## Fail-fast (K-section)

Every silent fallback became a typed error.

- `requiresenvironment` — missing package, optional dep.
- `requiresresource` — missing model / data / external resource.
- `configurationerror` — malformed config.
- `ioerror` — file/network problems.

The conformance harness treats typed errors as skips (`passed=True` with a
`skipped:` reason) so tests can run on a minimal sandbox while still catching
hard contract violations on stable concretes.

## Real backbones (L-section)

Backbones are no longer placeholders. `backbone:minicpm5`, `:llama32`, `:qwen25`,
`:pythia1` call `transformers.AutoModel.from_pretrained` for real. They fail-fast
via `requiresenvironment`/`requiresresource` when transformers is missing or the
Hub token is gated. On a CPU-only sandbox without network, the conformance
harness marks them skip-with-cause.

## Real quantizer (M-section)

The RVQ stack is real: `quantizer:quantizer` (residual VQ stack),
`:encoder` / `:decoder` (linear-MLP), `:semanticindex` (faiss IVF or in-mem
matmul), `:trainer` (real AdamW + MSE loop). The directory was renamed
`rqvae/` → `quantizer/` to remove opaque acronyms.

## Real rewards (N-section)

- `longtermreturn` — trainable MLP with `trainstep()` and AdamW; features are
  real (rating, kind flags, replay flag, tenure, recent activity).
- `diversitybonus`, `contenttypebalance`, `noveltyreward` — real math.
- `composite` — registered; weighted scalar with typed `requiresenvironment`.

## Real phases (O-section)

`phase:pretrain`, `:postrain`, `:reward`, `:codebook`, `:distill` each run a real
forward/backward loop.

## Composite loss (U-section)

`loss:braidedloss` no longer swallows term failures. Missing terms raise
`requiresenvironment`/`requiresresource` instead of silently passing zero.

## Tier-1 evaluators (S-section)

- `offlineranking`: MRR, NDCG@K, HitRate@K, MAP@K with parameterised cutoff.
- `calibration`: ECE, Brier, NLL, reliability table.
- `diversity`: intra-list pairwise distance, catalog coverage, Gini coefficient.
- `replay`: counterfactual replay delegating to offlineranking.
- `interleaving`: team-draft with 95 % confidence interval.
- `baseline`: random/popularity/TF-IDF comparison.
- `composite`: weighted scalar aggregation.

## Observability generation (X-section)

`python -m braid obsgen --out artifacts/obsgen` writes Prometheus rules, a
Grafana dashboard JSON and a metric catalogue by walking every registered
concrete's `observability()` and `metrics()`. 48 unique metrics across 146
concretes.

## CLI pipeline dispatch (V-section)

Every CLI subcommand is wired to its registered concrete:
* `data` → `data/ingest.py` ingest() pipeline
* `phase1` → `phase:pretrain`
* `rewards` → `phase:reward`
* `train` → `phase:postrain`
* `serve` → `server:vllm` or `server:hflocal`
* `eval` → `eval:offlineranking + :calibration + :diversity`
* `drift` → `drift:psi`
* `elbow` → `verbalizer/elbowfinder.run`
* `obsgen` → `core/obsgen.generate`

## Atomic commit policy

One logical change per commit. Final tally:

| Section | Description                | Commits |
| ------- | -------------------------- | ------- |
| A       | Quantizer dir + namespace  | 5       |
| B       | Phase rename                | 5       |
| C       | Indexer rename              | 4       |
| D       | Catalog store rename        | 1       |
| E       | Eval rename                 | 3       |
| F       | Curriculum rename           | 5       |
| G       | Batcher rename              | 4       |
| H       | Miner rename                | 5       |
| I       | Drift-response rename       | 1       |
| J       | Trim (kill k8s/kafka/...)   | 22      |
| K       | Fail-fast                    | 18      |
| L       | Real backbones              | 4       |
| M       | Real quantizer              | 4       |
| N       | Real rewards                | 5       |
| O       | Real phases                 | 5       |
| P       | Training loop                | 1       |
| Q       | Real serving                | 2       |
| T       | Metrics/log/secret          | 4       |
| V       | CLI dispatch                | 4       |
| W       | Real assertion tests        | 5       |
| X       | Observability generation    | 2       |
| U       | Composite loss + reward     | 2       |
| S       | Real evaluators             | 6       |
| R       | Real data ingest            | 1       |
| Y       | Docs                         | 1       |
| Z       | Final conformance           | 1       |
|         | **total**                    | **125** |
