lint:
    uv run ruff check

test:
    uv run pytest -v -s --cov=src tests

type:
    uv run ty check

publish:
    uv build --wheel
    uv publish
