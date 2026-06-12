## Goal

Add a selectable settlement method where the member with the largest net debt is responsible for outgoing remittances, and expose the selection through the `sharepay settle` CLI. Success means the current settlement behavior remains the default, the new max-debtor method can be chosen from Python and CLI, and tests document both methods.

## Context

`ExpenseGroup.settle_up()` previously calculated balances, then created relay-style transactions by making the largest debtor send their full owed amount to the largest creditor. That can require a net creditor to forward money to another creditor. The CLI called `group.settle_up()` without a method option.

## Architecture

Introduced `SettlementMethod` near `ExpenseGroup`, split the relay algorithm from the max-debtor hub algorithm, and kept the CLI thin by parsing the method option and passing it to `ExpenseGroup.settle_up()`.

## Non-Goals

- Do not change CSV or Google Sheet input formats.
- Do not change currency conversion, alias handling, balance display, or the default settlement behavior unless explicitly requested.

## Assumptions

- "The person who owes the most is responsible for remittance" means: choose the member with the largest positive net balance as a hub; the hub pays all net creditors, then other net debtors reimburse the hub.
- The CLI option can be named `--settlement-method`, with values `relay` for the current behavior and `max-debtor` for the new behavior.

## Plan

- [x] Add failing tests in `tests/test_expense_group.py` that define the max-debtor method: for balances `a=-100`, `b=-50`, `c=150`, `max-debtor` returns `c -> a 100` and `c -> b 50`; verified with `uv run pytest tests/test_expense_group.py -k max_debtor` (2 passed).
- [x] Add a multi-debtor test in `tests/test_expense_group.py` where the max debtor pays all creditors and the other debtor reimburses the max debtor; verified transaction order and zeroed applied balances with `uv run pytest tests/test_expense_group.py -k max_debtor` (2 passed).
- [x] Add a settlement-method enum or literal type in `src/sharepay/expense_group.py` to keep valid methods explicit and preserve `ExpenseGroup.settle_up()` default behavior; verified existing tests still call `settle_up()` without changes using `uv run pytest tests/test_expense_group.py tests/test_cli.py` (21 passed).
- [x] Refactor the existing `settle_up()` algorithm into a named internal path for the current relay method without behavior changes; verified existing settlement tests still pass with `uv run pytest tests/test_expense_group.py tests/test_cli.py` (21 passed).
- [x] Implement the max-debtor hub algorithm in `src/sharepay/expense_group.py`: reset/recalculate balances once, select the largest positive balance deterministically, create hub-to-creditor payments for every negative balance, then create other-debtor-to-hub reimbursements; verified with `uv run pytest tests/test_expense_group.py -k max_debtor` (2 passed).
- [x] Wire a Typer option in `src/sharepay/cli.py` such as `--settlement-method` to pass the chosen method into `group.settle_up()`; verified with `tests/test_cli.py::test_settle_settlement_method_max_debtor` and `uv run pytest tests/test_expense_group.py tests/test_cli.py` (21 passed).
- [x] Update `README.md` CLI and Python examples to mention the new settlement method and the default method; verified the documented command matches `uv run sharepay settle --help`, which shows `--settlement-method [relay|max-debtor] [default: relay]`.
- [x] Run quality gates from the repository root; verified with `just lint`, `just type`, `just test`, and `prek run -a`.

## Risks

- The requested business rule could mean a different hub flow than assumed; accepted by making the method behavior explicit in tests and docs.
- Floating-point residue can create tiny extra transactions; mitigated by reusing the existing `epsilon` threshold for debtor and creditor filtering.
- Changing `settle_up()` internals could accidentally alter existing transaction order; mitigated by preserving existing tests and adding method-specific tests.

## Completion Checklist

- [x] The current settlement method remains the default, verified by unchanged existing `tests/test_expense_group.py::test_expense_group_settle_up` and `tests/test_cli.py::test_settle_csv_file` results in `just test` (27 passed).
- [x] The max-debtor settlement method is available from Python, verified by `tests/test_expense_group.py::test_expense_group_settle_up_max_debtor_pays_each_creditor` and `tests/test_expense_group.py::test_expense_group_settle_up_max_debtor_collects_from_other_debtors`.
- [x] The max-debtor settlement method is available from CLI, verified by `tests/test_cli.py::test_settle_settlement_method_max_debtor`.
- [x] User-facing docs describe both methods and the CLI option, verified by `README.md` and `uv run sharepay settle --help` output.
- [x] Repository quality gates pass, verified by `just lint`, `just type`, `just test`, and `prek run -a`.
