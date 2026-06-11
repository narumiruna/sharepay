from __future__ import annotations

from pathlib import Path
from typing import Annotated

import httpx
import typer
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .balance import Balance
from .currency import Currency
from .expense_group import DEFAULT_CURRENCY
from .expense_group import ExpenseGroup
from .transaction import Transaction
from .utils import read_payment_csv

app = typer.Typer(help="Calculate sharepay settlement transactions.")


@app.callback()
def main() -> None:
    """Calculate sharepay settlement transactions."""


def _parse_aliases(alias_items: list[str] | None) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for item in alias_items or []:
        parts = item.split("=")
        if len(parts) != 2:
            msg = "Alias must use FROM=TO format."
            raise typer.BadParameter(msg)

        source = parts[0].strip().lower()
        target = parts[1].strip().lower()
        if not source or not target:
            msg = "Alias must use FROM=TO format."
            raise typer.BadParameter(msg)
        aliases[source] = target
    return aliases


def _normalized_balance_value(value: float, epsilon: float = 1e-6) -> float:
    if abs(value) <= epsilon:
        return 0
    return value


def _balance_style(value: float, epsilon: float = 1e-6) -> str:
    if value > epsilon:
        return "red"
    if value < -epsilon:
        return "green"
    return "dim"


def _balance_status(value: float, epsilon: float = 1e-6) -> Text:
    if value > epsilon:
        return Text("owes", style="red")
    if value < -epsilon:
        return Text("receives", style="green")
    return Text("settled", style="dim")


def _balance_amount(balance: Balance) -> Text:
    value = _normalized_balance_value(balance.value)
    return Text(f"{value:+.2f} {balance.currency}", style=_balance_style(value))


def _transaction_amount(transaction: Transaction) -> Text:
    return Text(f"{transaction.amount:.2f} {transaction.currency}", style="bold")


def _print_balances(console: Console, balances: list[Balance]) -> None:
    table = Table(title="Balances", box=box.ROUNDED)
    table.add_column("Member", style="bold")
    table.add_column("Balance", justify="right")
    table.add_column("Status")

    for balance in sorted(balances, key=lambda item: item.owner):
        table.add_row(Text(balance.owner), _balance_amount(balance), _balance_status(balance.value))

    console.print(table)


def _print_transactions(console: Console, transactions: list[Transaction]) -> None:
    if not transactions:
        console.print("[green]No transactions needed.[/green]")
        return

    table = Table(title="Settlement", box=box.ROUNDED)
    table.add_column("From", style="bold red")
    table.add_column("To", style="bold green")
    table.add_column("Amount", justify="right")

    for transaction in transactions:
        table.add_row(Text(transaction.sender), Text(transaction.recipient), _transaction_amount(transaction))

    console.print(table)


@app.command()
def settle(
    file: Annotated[
        Path | None,
        typer.Option(
            "--file",
            "-f",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="CSV file with amount, payer, members, and currency columns.",
        ),
    ] = None,
    sheet: Annotated[
        str | None,
        typer.Option("--sheet", "-s", help="Google Sheet sharing, CSV, or export URL with payment rows."),
    ] = None,
    currency: Annotated[
        Currency,
        typer.Option("--currency", "-c", case_sensitive=False, help="Settlement currency."),
    ] = DEFAULT_CURRENCY,
    alias: Annotated[
        list[str] | None,
        typer.Option("--alias", "-a", help="Alias in FROM=TO format. Can be provided multiple times."),
    ] = None,
) -> None:
    """Print the transactions needed to settle payments from a CSV file or Google Sheet."""
    if (file is None) == (sheet is None):
        msg = "Provide exactly one source: --file or --sheet."
        raise typer.BadParameter(msg)

    aliases = _parse_aliases(alias)
    try:
        if sheet is not None:
            group = ExpenseGroup.from_sheet(sheet, alias=aliases, currency=currency)
        elif file is not None:
            group = ExpenseGroup.from_df(read_payment_csv(file), alias=aliases, currency=currency)
        else:
            raise AssertionError("unreachable")

        transactions = group.settle_up()
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except httpx.HTTPError as exc:
        msg = f"HTTP request failed: {exc}"
        raise typer.BadParameter(msg) from exc
    console = Console()
    _print_balances(console, list(group.balances.values()))
    _print_transactions(console, transactions)


if __name__ == "__main__":
    app()
