.PHONY: help install api mobile test test-py test-js lint lint-py lint-js fmt typecheck compose-up compose-down clean

help:
	@echo "Targets:"
	@echo "  install      uv sync && pnpm install"
	@echo "  api          run FastAPI on :8000"
	@echo "  mobile       run Expo dev server"
	@echo "  test         run all tests"
	@echo "  lint         ruff + mypy + eslint"
	@echo "  fmt          ruff format + prettier"
	@echo "  compose-up   docker compose up (api + postgres)"

install:
	uv sync
	pnpm install

api:
	uv run --package phongthuy-api uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

mobile:
	pnpm --filter mobile start

test: test-py test-js

test-py:
	uv run pytest

test-js:
	pnpm -r test

lint: lint-py lint-js

lint-py:
	uv run ruff check .
	uv run mypy .

lint-js:
	pnpm -r lint
	pnpm -r typecheck

fmt:
	uv run ruff format .
	uv run ruff check --fix .
	pnpm -r format

typecheck:
	uv run mypy .
	pnpm -r typecheck

compose-up:
	docker compose -f infra/compose/dev.yml up --build

compose-down:
	docker compose -f infra/compose/dev.yml down

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	find . -type d -name .mypy_cache -prune -exec rm -rf {} +
	find . -type d -name .ruff_cache -prune -exec rm -rf {} +
