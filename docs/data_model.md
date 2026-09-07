# Data model

## Item schema (`item@v2`)

```yaml
itemid: int
title: str
genres: str          # comma-separated
year: int            # 1800..2100
```

Validated via Pandera when available. MovieLens-25M conforms.

## Event schema (`event@v2`)

```yaml
userid: int          # >= 0
itemid: int          # >= 0
kind: str            # play, thumbup, thumbdown, add, click
rating: float        # 0..5, nullable
duration: float      # seconds, >= 0, nullable
timestamp: float     # unix epoch seconds
```

## Context schema (`context@v1`)

```yaml
userid: str
metadata: dict       # arbitrary
ratelimitbudget: int
featureflags: dict[str, bool]
```

## Prompt schema (`prompt@v1`)

The verbalizer emits a single string. Variants differ by verbalizer name
(`eventsignal`, `narrative`, `structuredjson`, `compactelbow`,
`semanticsummary`).

## Rank request/response (`rankrequest@v1`, `rankresponse@v1`)

```yaml
rankrequest:
  userid: str
  context: dict
  history: list[event]
  candidates: list[int]
  topk: int          # default 50

rankresponse:
  ids: list[int]
  scores: list[float]
  fallback: bool
```

## Persistence

- `parquetsink` (default) writes a single Parquet file.
- `arrowsink` writes Arrow IPC.
- `postgressink` inserts via COPY.
- `parquetcflog` rotates Parquet files at configurable max rows.

All schemas are versioned under `braid.core.schema.simpleregistry`.
`migrate(name, raw, target)` walks versions forward.

## Splits

Three splitters available:
- `chronological` — by ratios.
- `leaveoneout` — per-user last-K as test.
- `timestratified` — per-bucket split then average.

## Configs

Every config file under `configs/` uses single-word field names with the
matching registry keys. To run a pipeline:

```bash
make data        # configs/data/movielens.yaml
make phase1      # configs/phase1/pretrain.yaml
make rewards     # configs/rewards/proxy.yaml
make train       # configs/train/phase2.yaml
make serve       # configs/serve/vllm.yaml
make eval        # configs/train/phase2.yaml
```
