.DEFAULT_GOAL := help
.PHONY: help setup data lint format test check clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

setup: ## Install dependencies and pre-commit hooks
	uv sync
	uv run pre-commit install

data: ## Download raw Olist data into data/raw/
	uv run python -m analyst.data.download

clean: ## Remove caches (safe, all rebuilt automatically)
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache

lint: ## Check code style without changing files
	uv run ruff check .
	uv run ruff format --check .

format: ## Auto-format code
	uv run ruff check --fix .
	uv run ruff format .

test: ## Run all tests
	uv run pytest

check: lint test ## Lint then test (run before committing)
