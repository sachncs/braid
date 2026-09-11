PYTHON ?= python3
PYTEST ?= pytest
RUFF ?= ruff
MYPY ?= mypy

.PHONY: help
help:
	@echo "braid — polymorphic LLM-backed recommendation ranker"
	@echo ""
	@echo "Targets:"
	@echo "  bootstrap      install deps + pre-commit hooks"
	@echo "  lint           run ruff"
	@echo "  format         run ruff format"
	@echo "  fmt-check      check ruff formatting without rewriting"
	@echo "  type           run mypy"
	@echo "  docstyle       run pydocstyle"
	@echo "  test           run all tests"
	@echo "  conformance    run conformance suite"
	@echo "  integration    run integration tests"
	@echo "  e2e            run end-to-end tests"
	@echo "  coverage       run tests with coverage report"
	@echo "  list           list registered components"
	@echo "  inspect        inspect a single component"
	@echo "  dryrun         validate a config without executing"
	@echo "  data           ingest MovieLens dataset"
	@echo "  phase1         run Phase-1 continued pretraining"
	@echo "  rewards        train reward proxy"
	@echo "  train          run Phase-2 post-training"
	@echo "  serve          start the ranker server"
	@echo "  eval           run evaluation suite"
	@echo "  drift          run drift detection"
	@echo "  elbow          context-length search"
	@echo "  obsgen         generate observability assets"
	@echo "  docker-build   build docker image"
	@echo "  docker-up      start docker compose"
	@echo "  docker-down    stop docker compose"
	@echo "  clean          remove build artifacts"
	@echo "  clean-all      clean plus artifacts, data and build dirs"

.PHONY: bootstrap
bootstrap:
	$(PYTHON) -m pip install -e ".[dev,serve]"
	$(PYTHON) -m pre_commit install

.PHONY: lint
lint:
	$(RUFF) check braid tests

.PHONY: format
format:
	$(RUFF) format braid tests

.PHONY: fmt-check
fmt-check:
	$(RUFF) format --check braid tests

.PHONY: type
type:
	$(MYPY) braid

.PHONY: docstyle
docstyle:
	$(PYTHON) -m pydocstyle braid

.PHONY: test
test:
	$(PYTEST) -q

.PHONY: conformance
conformance:
	$(PYTEST) -q -m conformance

.PHONY: integration
integration:
	$(PYTEST) -q -m integration

.PHONY: e2e
e2e:
	$(PYTEST) -q -m e2e

.PHONY: coverage
coverage:
	$(PYTEST) -q --cov=braid --cov-report=term-missing --cov-report=xml

.PHONY: status
status:
	$(PYTHON) scripts/status.py

.PHONY: list
list:
	$(PYTHON) -m braid list

.PHONY: inspect
inspect:
	@if [ -z "$(CAT)" ] || [ -z "$(NAME)" ]; then echo "usage: make inspect CAT=<category> NAME=<name>"; exit 1; fi
	$(PYTHON) -m braid inspect $(CAT) $(NAME)

.PHONY: dryrun
dryrun:
	$(PYTHON) -m braid dryrun --config $(CFG)

.PHONY: data
data:
	$(PYTHON) -m braid data --config configs/data/movielens.yaml

.PHONY: phase1
phase1:
	$(PYTHON) -m braid phase1 --config configs/phase1/pretrain.yaml

.PHONY: rewards
rewards:
	$(PYTHON) -m braid rewards --config configs/rewards/proxy.yaml

.PHONY: train
train:
	$(PYTHON) -m braid train --config configs/train/phase2.yaml

.PHONY: serve
serve:
	$(PYTHON) -m braid serve --config configs/serve/vllm.yaml

.PHONY: eval
eval:
	$(PYTHON) -m braid eval --config configs/train/phase2.yaml

.PHONY: drift
drift:
	$(PYTHON) -m braid drift

.PHONY: elbow
elbow:
	$(PYTHON) -m braid elbow --config configs/train/phase2.yaml

.PHONY: obsgen
obsgen:
	$(PYTHON) -m braid.obsgen --output grafana/

.PHONY: docker-build
docker-build:
	docker build -t braid:latest .

.PHONY: docker-up
docker-up:
	docker compose up -d

.PHONY: docker-down
docker-down:
	docker compose down

.PHONY: clean
clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage build dist
	find . -type d -name __pycache__ -exec rm -rf {} +

.PHONY: clean-all
clean-all: clean
	rm -rf artifacts data *.egg-info htmlcov coverage.xml
