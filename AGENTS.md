# Repository Guidelines

## Project Structure & Module Organization
Core library code lives in `src/sharepay/` and is split by domain modules (`payment.py`, `rate.py`, `debt.py`, `sharepay.py`, etc.).  
Tests are in `tests/` with one file per behavior area (for example, `tests/test_sharepay.py`).  
Example usage scripts are in `examples/` (`basic_usage.py`, `google_sheets.py`).  
Project metadata and tool configuration are centralized in `pyproject.toml`; automation workflows are under `.github/workflows/`.

## Build, Test, and Development Commands
- `uv sync` installs runtime and dev dependencies from `uv.lock`.
- `just lint` runs Ruff checks (`uv run ruff check`).
- `just type` runs static type checks (`uv run ty check`).
- `just test` runs pytest with coverage on `src` (`uv run pytest -v -s --cov=src tests`).
- `uv run pytest -k rate tests` is useful for focused test runs during iteration.
- `uv build --wheel` builds a distributable wheel (also used in publish workflow).

## Coding Style & Naming Conventions
Use Python 3.11+ features and keep code compatible with CI (Python 3.13).  
Follow Ruff defaults plus project rules: max line length `120`, import sorting with single-line imports, and strict lint families enabled in `pyproject.toml`.  
Use `snake_case` for functions/variables/modules, `PascalCase` for classes, and clear domain names matching existing modules.  
Run pre-commit hooks before opening a PR: `uv run prek run -a`.

## Testing Guidelines
Testing uses `pytest` and `pytest-cov`. Name tests `test_*.py` and functions `test_*`.  
Keep tests close to behavior boundaries (currency/rate/payment/sharepay).  
CI runs lint, type checks, and tests with coverage XML output; there is no hard coverage threshold configured, so avoid reducing effective coverage.  
Note: `test_query_rate` currently performs a live rate query, so network availability can affect local runs.

## Commit & Pull Request Guidelines
Recent history favors short, imperative commit messages (for example, `fix lint error`, `upgrade packages`, `remove Codecov upload step from CI workflow`).  
Keep commits scoped to one logical change.  
For PRs targeting `main`, ensure CI passes (`ruff`, `ty`, `pytest`), include a concise description, and link related issues when relevant.  
If behavior or examples change, update files in `examples/` or tests in the same PR.
