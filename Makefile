.PHONY: run test lint format fix

run:
	uv run uvicorn app.main:app --reload

test:
	uv run pytest -v

lint:
	uv run ruff check .

format:
	uv run ruff format .

fix:
	uv run ruff check . --fix
	uv run ruff format .
