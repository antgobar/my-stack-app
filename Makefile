.PHONY: install run test lint format fix

install:
	uv sync

run:
	uv run uvicorn app.main:app --reload

test:
	uv run pytest -v


format:
	uv run ruff check . --fix
	uv run ruff format .
