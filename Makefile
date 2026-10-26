.DEFAULT_GOAL := help
.PHONY: help setup lint format test check

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

setup: ## Install dependencies and pre-commit hooks
	uv sync
	uv run pre-commit install

lint: ## Check code style without changing files
	uv run ruff check .
	uv run ruff format --check .

format: ## Auto-format code
	uv run ruff check --fix .
	uv run ruff format .

test: ## Run all tests
	uv run pytest

check: lint test ## Lint then test (run before committing)
