# Computational Life — developer entry points.
# `make help` lists targets.

PYTHON ?= python3

.DEFAULT_GOAL := help
.PHONY: help install install-dev run test test-fast lint fmt cov clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## Install runtime deps
	$(PYTHON) -m pip install -r requirements.txt

install-dev:  ## Install runtime + dev deps and the package (editable)
	$(PYTHON) -m pip install -r requirements-dev.txt
	$(PYTHON) -m pip install -e .

run:  ## Run all four modules end to end
	$(PYTHON) -m complife

test:  ## Run the full test suite (includes slow Monte-Carlo checks)
	$(PYTHON) -m pytest

test-fast:  ## Run tests, skipping the slow Monte-Carlo sweeps
	$(PYTHON) -m pytest -m "not slow"

cov:  ## Run tests with coverage report
	$(PYTHON) -m pytest --cov=complife --cov-report=term-missing

lint:  ## Static checks
	$(PYTHON) -m ruff check complife tests

fmt:  ## Auto-fix lint issues
	$(PYTHON) -m ruff check --fix complife tests

clean:  ## Remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
