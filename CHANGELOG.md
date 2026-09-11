# Changelog

All notable changes to braid are documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Initial polymorphic spine, registry, capabilities, lifecycle.
- Real backbones (`MiniCPM-5`, `Llama 3.2`, `Qwen 2.5`, `Pythia-1B`).
- Real quantizer (residual VQ + encoder/decoder + semantic index).
- Real rewards (long-term return, diversity bonus, novelty, content-type balance).
- Real phases (pretrain, post-train, reward proxy, codebook, distill).
- Braided loss + composite reward + composite eval.
- Tier-1 evaluators (offline-ranking, calibration, diversity, replay, interleaving, baseline).
- Observability generator (Prometheus rules + Grafana dashboard).
- FastAPI serving layer.
- Entry-point-based concrete registration via `registry.loadentrypoints()`.
- `serve` extra with `fastapi`, `uvicorn`, `prometheus-client`.
- `make fmt-check`, `make coverage`, `make clean-all` targets.
- Typed-error propagation in `datasink`, `datasource`, `catalogstore` paths.

### Changed
- Restructured ruff rule set to `E, F, W` with per-file `E501` ignore.
- Conformance harness now reports real-pass and skip counts separately.
- `configs/train/phase2.yaml` uses current registry names (`composite`, `checkpoint`).
- `configs/serve/vllm.yaml` uses `tracing: console` (the removed `tracing: otlp`).
- Datasinks treat `path` as a directory and emit `rows.arrow` / `rows.parquet`.

### Fixed
- `localparquet` raises `requiresenvironment` when `pyarrow` is missing.
- `faissivfstore` raises `requiresenvironment` when `faiss` is missing.
- `drift` CLI no longer requires `--config`.
- Duplicate `lmax` branch removed from `braidedloss.compute`.
- `docker-compose.yml` no longer references removed services.
- Bootstrap / Dockerfile reference the existing `serve` extra, not the missing `all` extra.
- CI workflows no longer mask failures with `|| true`.

### Removed
- Stub-only concretes that required Kubernetes / Kafka / Postgres / commercial inference engines.
- Silent fallbacks; missing deps now raise typed `requiresenvironment`.
