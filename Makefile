setup:
	uv sync --locked
data:
	uv run rnv fetch
all:
	uv run rnv run
	uv run rnv publish
test:
	uv run ruff check .
	uv run ruff format --check .
	uv run pytest
