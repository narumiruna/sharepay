from __future__ import annotations

from pathlib import Path
from typing import Annotated

import httpx
import typer

from .currency import Currency
from .expense_group import DEFAULT_CURRENCY
from .expense_group import ExpenseGroup
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
        typer.Option("--sheet", "-s", help="Google Sheet CSV/export URL with payment rows."),
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
    if not transactions:
        typer.echo("No transactions needed.")
        return

    for transaction in transactions:
        typer.echo(str(transaction))


if __name__ == "__main__":
    app()
