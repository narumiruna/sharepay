# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SharePay is a Python library for splitting expenses and calculating who owes whom in group payments. It supports multiple currencies with automatic exchange rate conversion and can import data from Google Sheets.

The project now includes a **FastAPI web application** (`src/sharepay_web/`) that provides a user-friendly interface for expense tracking and settlement calculations.

## Development Commands

### Linting and Formatting
```bash
# Run ruff linter
make lint
# or
uv run ruff check .

# Run type checking
uv run mypy src/
```

### Testing
```bash
# Run all tests with coverage
make test
# or
uv run pytest -v -s --cov=src tests

# Run specific test file
uv run pytest tests/test_sharepay.py -v
uv run pytest tests/test_payment.py -v
uv run pytest tests/test_rate.py -v
uv run pytest tests/test_web.py -v

# Run specific test function
uv run pytest tests/test_sharepay.py::test_function_name -v

# Run tests matching pattern
uv run pytest -k "test_pattern" -v
```

### Web Application
```bash
# Start the web application
make web
# or
uv run python scripts/run_web.py
# or
uv run uvicorn src.sharepay_web.main:app --host 0.0.0.0 --port 8000 --reload
```

### Building and Publishing
```bash
# Build wheel
make publish
# or
uv build --wheel
uv publish
```

## Architecture

### Core Components

- **SharePay** (`src/sharepay/sharepay.py`): Main class that manages expense splitting
  - Handles payments, balances, and debt calculations
  - Supports multiple currencies with exchange rate conversion
  - Can import from pandas DataFrame or Google Sheets
  - Implements settlement algorithm to minimize transactions

- **Payment** (`src/sharepay/payment.py`): Represents a single expense payment
  - Contains amount, currency, payer, and list of members
  - Automatically calculates individual debts for each member

- **Currency** (`src/sharepay/currency.py`): Enum defining supported currencies
  - Currently supports: EUR, GBP, JPY, TWD, USD, CAD

- **Balance** (`src/sharepay/balance.py`): Tracks individual member balances
- **Debt** (`src/sharepay/debt.py`): Represents debt between two members
- **Transaction** (`src/sharepay/transaction.py`): Final settlement transactions
- **Rate** (`src/sharepay/rate.py`): Exchange rate querying functionality
- **Utils** (`src/sharepay/utils.py`): Utility functions including Google Sheets integration

### Web Application Components

- **Main App** (`src/sharepay_web/main.py`): FastAPI application with all routes
- **Database Models** (`src/sharepay_web/database.py`): SQLAlchemy models for users, trips, payments
  - SQLite database file: `travel_expenses.db` (auto-created in project root)
- **Authentication** (`src/sharepay_web/auth.py`): JWT-based authentication system with refresh tokens
- **Schemas** (`src/sharepay_web/schemas.py`): Pydantic models for API request/response validation
- **Templates** (`src/sharepay_web/templates/`): Jinja2 HTML templates
- **Static Files** (`src/sharepay_web/static/`): CSS, JavaScript, and other assets

### Key Features

1. **Multi-currency support**: Automatic conversion using live exchange rates
2. **Google Sheets integration**: Import expense data directly from spreadsheets
3. **Alias support**: Map different names to the same person
4. **Settlement optimization**: Minimize number of transactions needed
5. **Logging**: Uses loguru for transaction logging
6. **Web Interface**: FastAPI-based web application with responsive UI
7. **User Management**: Registration, authentication, and trip collaboration
8. **Mixed Member Types**: Support for both registered users and guest members

### Data Flow

1. Add payments via `add_payment()` or import from Google Sheets
2. Each payment generates debts between payer and other members
3. `settle_up()` calculates optimal transactions to balance all debts
4. Exchange rates are applied when converting between currencies

## Testing

The project uses pytest with coverage reporting. Test files are located in `tests/` directory and follow the naming convention `test_*.py`.

## Dependencies

### Core Library
- **pydantic**: Data validation and settings management
- **pandas**: Data manipulation for Google Sheets import
- **httpx**: HTTP client for API requests
- **loguru**: Structured logging
- **click**: Command-line interface (if CLI features are added)

### Web Application
- **fastapi**: Modern web framework for building APIs
- **uvicorn**: ASGI web server
- **jinja2**: Template engine for HTML rendering
- **python-multipart**: Form data parsing
- **sqlalchemy**: ORM for database operations
- **python-jose**: JWT token handling
- **passlib**: Password hashing with bcrypt
- **email-validator**: Email validation utilities

## Code Style

- Uses ruff for linting and formatting
- Line length: 120 characters
- Import sorting: force single-line imports
- Type hints required (mypy checking enabled)
- Modern Python features: uses `|` union syntax, `list[T]` generics
- SQLAlchemy 2.0+ with DeclarativeBase
- Pre-commit hooks enabled: runs ruff, ruff-format, and other checks automatically

## Development Setup

```bash
# Install dependencies
uv sync

# Install pre-commit hooks (optional but recommended)
uv run pre-commit install

# Manual pre-commit check
uv run pre-commit run --all-files
```
