# Repository Guidelines

## Project Structure & Scope
- `sharepay` is a uv-managed Python package and Typer CLI. Core code lives in `src/sharepay/` (`expense_group.py`, `payment.py`, `rate.py`, `cli.py`, etc.).
- Tests live in `tests/` with `test_*.py` files; examples live in `examples/`.
- Keep project metadata in `pyproject.toml` and dependency resolution in `uv.lock`. Use uv commands for dependency changes; do not hand-edit `uv.lock`.
- Do not edit generated or local-only artifacts such as `.venv/`, `.ruff_cache/`, `.pytest_cache/`, `__pycache__/`, `.coverage`, `dist/`, or local `*.db` files.

## Build, Test, and Development Commands
Run commands from the repository root.
- `uv sync` installs runtime and dev dependencies from `uv.lock`.
- `just lint` runs `uv run ruff check`.
- `just type` runs `uv run ty check`.
- `just test` runs `uv run pytest -v -s --cov=src tests`.
- `uv run pytest -k rate tests` is a useful focused test example.
- `prek run -a` runs the configured hooks (`ruff`, `ruff-format`, `uv-lock`, `ty-check`, `tombi-format`, and whitespace/YAML checks); run it before finishing any change.
- `uv build --wheel` builds the package wheel. Do not run `uv publish` or `just publish` unless explicitly asked.

## Coding Style & Conventions
- Keep code compatible with `requires-python >=3.11`; CI currently runs Python 3.13.
- Follow Ruff settings in `pyproject.toml`: line length 120, single-line imports, and the enabled lint families.
- Use `snake_case` for modules, functions, and variables; `PascalCase` for classes; and domain names consistent with existing modules (`ExpenseGroup`, `Payment`, `Rate`, `Transaction`).
- Keep CLI behavior in `src/sharepay/cli.py` covered by tests using Typer's `CliRunner` when command output changes.

## Testing and Verification
- Add or update tests when behavior changes. Keep tests near the behavior area (`test_cli.py`, `test_rate.py`, `test_payment.py`, etc.).
- `tests/test_rate.py::test_query_rate` performs a live exchange-rate query, so local failures can be network-related.
- CI runs Ruff, ty, and pytest with coverage XML on pull requests and pushes to `main`; there is no hard coverage threshold, but avoid reducing meaningful coverage.

## Security, Configuration, and PR Notes
- Never commit secrets, API tokens, credentials, `.env` files, local databases, or publish tokens. Publish uses GitHub secrets (`PYPI_TOKEN`) in workflow context.
- Keep commits scoped to one intent. Recent history uses short imperative messages and occasional Conventional Commit prefixes.
- For PRs targeting `main`, include a concise summary and verification results; mention examples or CLI output changes when relevant.
