# Evaluation guide

7 evaluators + 1 composite, plus significance tests.

## Offline

`eval:offlineranking` computes MRR, NDCG@10, HitRate@10, MAP@10 from
`(predictions, ground_truth)` pairs.

```python
ev = braid.registry.create("eval", "offlineranking")
report = ev.evaluate([[3, 1, 2], [1, 2, 3]], [1, 1])
# → {"mrr": ..., "ndcg": ..., "hitrate": ..., "map": ...}
```

## Calibration

`eval:calibration` returns Expected Calibration Error (ECE) and per-bin
reliability stats.

## Diversity

`eval:diversity` (intralist diversity, coverage). Pass `embeddings` for
intra and `universe` for coverage.

## Replay

`eval:replay` runs a saved ranker over historical queries and measures
recall vs actual engagement.

## Interleaving

`eval:interleaving` implements team-draft. Call
`interleave(lista, listb) -> (combined, owners)`. Pass query-level
`engagements` to compute wins per team.

## Baseline comparison

`eval:baseline` compares the ranker to random + popularity (if `popularity`
is provided).

## Composite

`eval:composite` runs multiple evaluators on shared inputs and merges
their reports into a single dict.

```yaml
eval:
  type: composite
  members:
    - type: offlineranking
      weight: 1.0
    - type: calibration
      weight: 0.5
    - type: diversity
      weight: 0.5
    - type: interleaving
      weight: 0.7
```

## Reporters

- `htmlreporter.visitreport` renders HTML.
- `jsonreporter.visitreport` emits JSON.
- `mdreporter.visitreport` emits Markdown.
- `csvreporter.visitreport` emits CSV.

## Significance

`eval:composite` includes bootstrap CI for paired t-test vs baseline.

## Online A/B

`router:stickybucketrouter` + `eval:interleaving` give you shadow-mode
testing without affecting responses:

```python
router = braid.registry.create("router", "shadowrouter", arms=["control", "treatment"])
arm = router.route(userid)  # always "control"
shadowrank = ranker.rank(prompt, ..., usermode=router.shadowroute(userid))
log = braid.registry.create("cflog", "parquetcflog", dir="cf/")
log.log({"userid": userid, "control": controlresponse, "treatment": shadowrank})
# offline analyze with eval:replay or eval:interleaving
```
