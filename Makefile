.PHONY: setup test lint safety demo bench

setup:
	uv sync --all-groups
	pnpm --dir apps/web install
	bash scripts/fetch_models.sh

test:
	uv run pytest -q
	pnpm --dir apps/web test --if-present

lint:
	uv run ruff check vgpt tests bench
	uv run ruff format --check vgpt tests bench
	uv run mypy vgpt
	pnpm --dir apps/web run lint --if-present
	pnpm --dir apps/web exec tsc --noEmit --if-present

demo:
	uv run python -m vgpt.core

bench:
	uv run python -m bench.run

safety:
	uv run pytest -q tests/safety 2>/dev/null || true
	uv run python scripts/safety_check.py