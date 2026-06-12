# sharepay — split expenses, settle debts, and convert currencies

`sharepay` is a Python expense-splitting library and command-line tool for group trips, shared bills, and
reimbursements. Import expenses from CSV or Google Sheets, split each payment across members, convert currencies with
live exchange rates, and print the transactions needed to settle up.

## Features

- Split group expenses equally across payment members.
- Calculate who owes whom and produce settlement transactions.
- Choose default relay settlement or max-debtor settlement, where the largest net debtor coordinates remittances.
- Import payments from CSV files or public Google Sheets.
- Convert multi-currency expenses into one settlement currency.
- Merge duplicate people with aliases such as `johnny=john`.
- Use as a Typer CLI or as a Python library.

## Installation

Requires Python 3.11 or newer.

```bash
pip install sharepay
```

For local development from this repository:

```bash
uv sync
uv run sharepay --help
```

## Quick start: settle expenses from CSV

Create an `expenses.csv` file with the required columns: `amount`, `payer`, `members`, and `currency`.

```csv
amount,payer,members,currency
300,alice,"alice,bob,cara",TWD
200,bob,"bob,cara",TWD
```

Run the settlement calculator:

```bash
sharepay settle --file expenses.csv --currency TWD
```

`sharepay` prints member balances and the transactions needed to settle the group.

## Google Sheets import

Use a public Google Sheets sharing URL, CSV URL, or export URL with the same payment columns:

```bash
sharepay settle \
  --sheet "https://docs.google.com/spreadsheets/d/<sheet-id>/edit#gid=0" \
  --currency TWD
```

The sheet is read as CSV. Make sure it contains:

| Column | Description |
| --- | --- |
| `amount` | Payment amount, with optional thousands separators |
| `payer` | Person who paid |
| `members` | Comma-separated people sharing the payment |
| `currency` | Payment currency code |

## Common CLI options

```bash
sharepay settle --file expenses.csv
sharepay settle \
  --sheet "https://docs.google.com/spreadsheets/d/<sheet-id>/edit#gid=0"
sharepay settle --file expenses.csv --currency USD
sharepay settle --file expenses.csv --settlement-method max-debtor
sharepay settle --file expenses.csv --alias "johnny=john" --alias "jon=john"
```

Supported settlement currencies are `EUR`, `GBP`, `JPY`, `TWD`, `USD`, and `CAD`. The default settlement currency is
`TWD`.

## Settlement methods

`sharepay settle` uses `--settlement-method relay` by default, preserving the original settlement flow where one member
may receive money and forward part of it to another member. Use `--settlement-method max-debtor` when the member with the
largest net debt should send money to every net creditor first; other debtors then reimburse that member.

## Python API example

```python
from sharepay import Currency
from sharepay import ExpenseGroup

group = ExpenseGroup(name="trip", currency=Currency.TWD)
group.add_payment(
    amount=300,
    currency=Currency.TWD,
    payer="alice",
    members=["alice", "bob", "cara"],
)
group.add_payment(
    amount=200,
    currency=Currency.TWD,
    payer="bob",
    members=["bob", "cara"],
)

for transaction in group.settle_up():
    print(transaction)
```

Use `group.settle_up(method="max-debtor")` to choose the max-debtor method from Python.

Output:

```text
cara   -> alice      200.00 TWD
```

## How sharepay works

1. Each payment is split equally among the listed `members`.
2. The payer is credited for the shares paid on behalf of others.
3. Expenses in other currencies are converted into the settlement currency with live exchange rates.
4. Optional aliases canonicalize repeated names before balances are settled.
5. `settle_up()` returns the transactions needed to bring balances back to zero, using relay settlement by default or
   max-debtor settlement when selected.

## Development

Useful commands from the repository root:

```bash
uv sync
just lint
just type
just test
prek run -a
```

CI runs Ruff, ty, and pytest on Python 3.13. Before publishing, build a wheel with:

```bash
uv build --wheel
```

## License

MIT License.
