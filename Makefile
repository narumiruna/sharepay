install:
	poetry install

lint:
	poetry run ruff check .

test:
	poetry run pytest -v -s --cov=sharepay --cov-report=xml tests

publish:
	poetry build -f wheel
	poetry publish

.PHONY: lint test publish
