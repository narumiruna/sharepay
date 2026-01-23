lint:
	uv run ruff check

test:
	uv run pytest -v -s --cov=src tests

type:
	uv run ty check

publish:
	uv build --wheel
	uv publish

web:
	@echo "🚀 啟動旅行支出分帳網站..."
	@echo "訪問 http://localhost:8000 查看網站"
	uv run python run_web.py

.PHONY: lint test publish web
