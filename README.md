# braid

> Braiding signals into ranks. A polymorphic LLM-backed recommendation ranker inspired by Netflix's GenRec.

`braid` is an end-to-end library for **verbalized, multi-reward, catalog-aware recommendation ranking** built on a polymorphic spine. Every primitive — backbones, catalog stores, verbalizers, rewards, losses, evaluators, monitoring — is registry-dispatched and configurable from a single Pydantic config.

## Highlights

- **Polymorphic spine** with six layers: registry, traits, lifecycle, capability, versioning, schema, observability, context.
- **140 real concrete implementations** across 42 categories — no stubs.
- **Single-word identifiers** end-to-end (no snake_case, no camelCase, no `_` prefixes).
- **Three braided composites** — `braidedloss`, `compositereward`, `compositeeval` — composed via the registry.
- **Real reward modeling**, **RQ-VAE semantic IDs**, **full-catalog matmul ranking**, **vLLM prefill-only serving**.
- **Production-grade monitoring**: Prometheus metrics, OpenTelemetry tracing, PSI/KS/JSD drift detection, Grafana dashboards.

## Quick start

```bash
make bootstrap
make data          # MovieLens-25M ingest
make phase1        # continued pretraining
make rewards       # long-term-return proxy
make train         # Phase-2 post-training
make serve         # vLLM prefill-only ranker
make eval          # offline metrics + replay + interleaving
```

## Documentation

See `docs/` for architecture, per-category extension guides, and the decision log. Run `braid list` to introspect all registered components.

## License

MIT
