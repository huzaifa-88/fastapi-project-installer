.DEFAULT_GOAL := help
.PHONY: help install local-setup dev dev-down lint format test check clean

PLAYGROUND := .playground
DEMO_NAME  := demo-app
DEMO_SLUG  := demo_app
DEMO_DIR   := $(PLAYGROUND)/$(DEMO_NAME)
DEV_STACK  := fastapi-installer-dev
# Host port for the demo Postgres; override if taken: make dev DEV_DB_PORT=5432
DEV_DB_PORT ?= 55432

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install all project dependencies (including dev tools)
	uv sync

local-setup: ## One-time setup for developers: deps, git repo, git hooks
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed: https://docs.astral.sh/uv/getting-started/installation/"; exit 1; }
	uv python install
	$(MAKE) install
	@[ -d .git ] || git init
	git config core.hooksPath .githooks
	chmod +x .githooks/*
	@echo "Local setup complete. Run 'make dev' to try a generated project."

dev: ## Generate a fresh demo project, start its Postgres, migrate, and run the dev server
	@[ ! -d $(DEMO_DIR) ] || (cd $(DEMO_DIR) && docker compose -p $(DEV_STACK) down -v)
	rm -rf $(DEMO_DIR)
	uv run fastapi-installer new $(DEMO_NAME) -y -o $(DEMO_DIR)
	cd $(DEMO_DIR) && sed 's/^POSTGRES_PORT=.*/POSTGRES_PORT=$(DEV_DB_PORT)/' .env.example > .env
	cd $(DEMO_DIR) && uv sync
	cd $(DEMO_DIR) && docker compose -p $(DEV_STACK) up -d db --wait
	cd $(DEMO_DIR) && uv run alembic upgrade head
	cd $(DEMO_DIR) && uv run fastapi dev src/$(DEMO_SLUG)/main.py

dev-down: ## Stop the demo project's Postgres and delete its data
	@[ ! -d $(DEMO_DIR) ] || (cd $(DEMO_DIR) && docker compose -p $(DEV_STACK) down -v)

lint: ## Run ruff lint (incl. import order) and format check
	uv run ruff check .
	uv run ruff format --check .

format: ## Auto-fix lint issues, sort imports and format code
	uv run ruff format .
	uv run ruff check --fix .

test: ## Run the test suite
	uv run pytest

check: lint test ## Run everything a commit must pass

clean: dev-down ## Remove caches, build output and the playground
	rm -rf $(PLAYGROUND) dist build .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -not -path "./.venv/*" -prune -exec rm -rf {} +
