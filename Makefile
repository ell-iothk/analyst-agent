.DEFAULT_GOAL := help
.PHONY: help setup lint format test check

help: ## Tampilkan daftar perintah
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

setup: ## Pasang library dan pre-commit hook
	uv sync
	uv run pre-commit install

lint: ## Cek gaya kode tanpa mengubah apa pun
	uv run ruff check .
	uv run ruff format --check .

format: ## Rapikan kode otomatis
	uv run ruff check --fix .
	uv run ruff format .

test: ## Jalankan semua test
	uv run pytest

check: lint test ## Lint lalu test (jalankan sebelum commit)
