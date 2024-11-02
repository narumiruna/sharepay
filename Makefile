lint:
	uv run ruff check .

test:
	uv run pytest -v -s --cov=src tests

publish:
	uv build --wheel
	uv publish

.PHONY: lint test publish
