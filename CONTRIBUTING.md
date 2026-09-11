# Contributing to braid

Thanks for your interest in braid. This document explains how to set up
the project locally, run the test suite, and submit a pull request.

## Reporting issues

Open an issue at
[`sachncs/braid/issues`](https://github.com/sachncs/braid/issues)
using the appropriate template (`bug`, `feature_request`, or `question` via
Discussions if enabled). For security issues, follow
[`SECURITY.md`](./SECURITY.md).

## Development setup

```
python -m venv .venv
source .venv/bin/activate
make bootstrap       # pip install -e ".[dev,serve]" + pre-commit install
```

The `serve` extra pulls in `fastapi`, `uvicorn`, and `prometheus-client`
for the runtime server (`make serve`, `python -m braid serve`).

## Tests

```
make test                 # full pytest run
make conformance          # sweeps every registered concrete (-m conformance)
make integration          # registry / phase / loss / reward / e2e contracts (-m integration)
make e2e                  # CLI / pipeline smoke tests (-m e2e)
make status               # prints live category / concrete / conformance / test counts
```

## Lint / format / type / docstyle

```
make lint           # ruff check braid tests scripts
make fmt-check      # ruff format --check (read-only)
make format         # rewrite files to match the declared style
make type           # mypy braid
make docstyle       # pydocstyle braid
```

The project pins the ruff rule set to `E, F, W` and ignores `E501`
line-length per file. mypy and pydocstyle currently run with `|| true`
in CI while upstream-library type-statement and numpy-convention
docstring noise is triaged; please don't introduce new violations.

## Coding conventions

- One lowercase word per identifier — no `snake_case`, no `camelCase`,
  no `_` prefixes. See `docs/decision_log.md` for the rename table.
- Numpy-style docstrings on every concrete.
- Mandatory on every concrete: `name`, `version`, `capabilities`,
  `__init__`, `observability()`, `metrics()`.
- Add `idempotencykey()` if you declare `idempotent`.
- Add `cacheget`/`cacheput`/`cacheinvalidate` if you declare `cachable`.
- Add `persist`/`restore` if you declare `persistable`.
- Add `shardrank`/`numshards` if you declare `distributable`.

## Adding a new concrete

Follow [`docs/extension_guide.md`](./docs/extension_guide.md). New
backbones / catalog stores can also be registered via the entry-point
mechanism documented there — `registry.loadentrypoints()` is called
from `braid/__init__.py`.

## Pull request flow

1. Fork the repository.
2. Create a topic branch off `master` (use linear history).
3. Make focused commits with clear messages (`fix:`, `feat:`, `docs:`,
   `refactor:`, `test:`, or `style:` prefixes).
4. Ensure `make test`, `make lint`, and `make fmt-check` all pass.
5. Add a `Closes #NNN` line referencing the issue your PR fixes.
6. Use the [PR template](./.github/PULL_REQUEST_TEMPLATE.md).
7. Push the branch and open a pull request targeting `master`.

By submitting a pull request, you agree to follow the
[Code of Conduct](./CODE_OF_CONDUCT.md).
