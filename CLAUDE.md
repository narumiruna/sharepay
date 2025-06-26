# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SharePay is a Python library for splitting expenses and calculating who owes whom in group payments. It supports multiple currencies with automatic exchange rate conversion and can import data from Google Sheets.

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

### Key Features

1. **Multi-currency support**: Automatic conversion using live exchange rates
2. **Google Sheets integration**: Import expense data directly from spreadsheets
3. **Alias support**: Map different names to the same person
4. **Settlement optimization**: Minimize number of transactions needed
5. **Logging**: Uses loguru for transaction logging

### Data Flow

1. Add payments via `add_payment()` or import from Google Sheets
2. Each payment generates debts between payer and other members
3. `settle_up()` calculates optimal transactions to balance all debts
4. Exchange rates are applied when converting between currencies

## Testing

The project uses pytest with coverage reporting. Test files are located in `tests/` directory and follow the naming convention `test_*.py`.

## Dependencies

- **pydantic**: Data validation and settings management
- **pandas**: Data manipulation for Google Sheets import
- **httpx**: HTTP client for API requests
- **loguru**: Structured logging
- **click**: Command-line interface (if CLI features are added)

## Code Style

- Uses ruff for linting and formatting
- Line length: 120 characters
- Import sorting: force single-line imports
- Type hints required (mypy checking enabled)