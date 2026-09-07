# Monitoring guide

Three metrics backends, four drift detectors, three drift responses,
three tracing backends, three log backends, three secret providers.

## Metrics

`metrics:prometheus`, `metrics:otelotlp`, `metrics:statsd` are all
registered concretes. Each exposes:

```python
def counter(self, name, value=1.0, labels=None): ...
def gauge(self, name, value, labels=None): ...
def histogram(self, name, value, labels=None): ...
```

The `obsgen` CLI generates Prometheus alert rules + Grafana dashboards
from every concrete's `observability()` declaration.

## Drift detection

| Detector | What |
|---|---|
| `drift:psi` | Population Stability Index |
| `drift:ks` | Kolmogorov-Smirnov |
| `drift:jsd` | Jensen-Shannon divergence |
| `drift:pagehinkley` | Sequential change-point |

Each registers under `drift:*`. The CLI subcommand `braid drift` runs the
detector on the configured reference vs the live distribution.

## Drift response

Three responses:
- `driftresponse:alert` — log warning.
- `driftresponse:retraintrigger` — write a trigger file.
- `driftresponse:fallbackbaseline` — toggle a fallback flag.

## Tracing

3 backends: `otlp`, `jaeger`, `console`. The server uses
`tracing.span(name, **attrs)` as a context manager.

## Logs

3 backends: `structlogjson`, `logfmt`, `plain`. Configurable via env
`BRAID_LOG_FORMAT` and `BRAID_LOG_LEVEL`.

## Secrets

3 providers: `env` (default), `vault` (HashiCorp), `k8s` (K8s API).

```python
secret = braid.registry.create("secret", "vault", url="...", token="...")
value = secret.get("db/password", key="password")
```

## Drift workflow

```bash
braid list drift                                  # 4 detectors
braid list driftresponse                          # 3 responses
braid dryrun --config configs/drift/psi.yaml      # what would happen
```

`make obsgen` materializes Prometheus rules + alerts.

## Grafana

`grafana/dashboards/braid.json` (generated) plus
`grafana/alerts.yml` are ready to import. Dashboards auto-update from
declared observability.

## Health & readiness

```
GET /health   # → {"status": "live"}
GET /ready    # → {"ready": true, "details": {...}}
```

Each is computed via the `lifecycle` Protocol's `health()` method,
dispatched through `lifecycledelegate`.
