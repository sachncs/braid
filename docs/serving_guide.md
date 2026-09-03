# Serving guide

`braid` ships a FastAPI app (`braid.serving.app.createapp`) plus four
server backends, three caches, four auth backends, three rate limiters,
three preprocessors, and three postprocessors — all swap-in via the
registry.

## Quick start

```bash
make serve                # spins up vLLM prefill-only ranker
curl localhost:8080/health  # {"status":"live"}
curl -X POST localhost:8080/rank \
  -H "content-type: application/json" \
  -d '{"userid":"alice","context":{},"candidates":[1,2,3,4,5],"topk":3}'
```

## Server backends

| Name | What |
|---|---|
| `vllm` | vLLM prefill-only with catalog-matmul scoring |
| `triton` | Triton Inference Server backend |
| `hflocal` | Local HF model (CPU/dev-friendly) |
| `openaicompat` | OpenAI Chat Completions as a ranker |

## Endpoints

| Path | Method | Purpose |
|---|---|---|
| `/health` | GET | Liveness probe |
| `/ready` | GET | Readiness probe |
| `/metrics` | GET | Prometheus scrape endpoint |
| `/rank` | POST | Run a ranking request |

## Default config

`configs/serve/vllm.yaml` is the reference config. The `createapp`
factory takes concrete instances as kwargs:

```python
from braid.serving.app import createapp
app = createapp(
    server=braid.registry.create("server", "vllm", model="openbmb/MiniCPM5-1B"),
    catalogstore=braid.registry.create("catalogstore", "matmulinmem", embeddings=e),
    cache=braid.registry.create("cache", "lru", maxentries=10_000),
    auth=braid.registry.create("auth", "apikey", allowed=[...]),
    ratelimit=braid.registry.create("ratelimit", "tokenbucket", rate=1000),
    reqpres=[braid.registry.create("reqpre", "normalize"), braid.registry.create("reqpre", "validate")],
    respposts=[braid.registry.create("resppost", "calibrate"), braid.registry.create("resppost", "diversity")],
    metrics_backend=braid.registry.create("metrics", "prometheus"),
)
```

Or load from a YAML config.

## Prefix KV-cache

```python
from braid.serving.prefixcache import prefixcache
pc = prefixcache()
pc.put("system:rec", encoded_kv)
# ... retrieve pc.get("system:rec") on each request to reuse
```

## Lifecycle

`braid.serving.lifecycle.lifecycleserver` wraps a `RankServer` concrete
with SIGTERM/SIGINT handling and graceful shutdown.

## Catalog scoring

The prefill-only path: vLLM encodes the prompt in one pass; the catalog
score is `h @ E.T` (one BLAS call) for catalogs ≤ ~1M items. Larger
catalogs swap in `faissivfstore` or `catalogstore:hnsw`.

## Response caching

`cache:lru` for in-process, `cache:redis` for multi-replica. The `rank`
endpoint keys cache by `(userid, requestid)` with TTL configurable.

## Observability

`metrics:prometheus` exposes counters, histograms, gauges via the
`/metrics` endpoint. `obsgen` walks the registry and generates dashboards
+ alerts.

## A/B routing

`router:stickybucketrouter` hashes the user id to an arm. `shadowrouter`
runs treatment in parallel without affecting responses.
