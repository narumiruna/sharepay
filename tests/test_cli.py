import re
from pathlib import Path

import httpx
from typer.testing import CliRunner

from sharepay import utils
from sharepay.cli import app

runner = CliRunner()


class _FakeSheetResponse:
    content = b'amount,payer,members,currency\n300,a,"a,b,c",TWD\n200,b,"b,c",TWD\n'

    def raise_for_status(self) -> None:
        pass


def _write_payments_csv(tmp_path: Path, content: str) -> Path:
    csv_path = tmp_path / "payments.csv"
    csv_path.write_text(content)
    return csv_path


def _assert_balance(output: str, member: str, amount: str, status: str) -> None:
    assert re.search(rf"│ {re.escape(member)}\s+│\s+{re.escape(amount)} │ {re.escape(status)}\s+│", output)


def _assert_no_balance(output: str, member: str) -> None:
    assert not re.search(rf"│ {re.escape(member)}\s+│", output)


def _assert_settlement(output: str, sender: str, recipient: str, amount: str) -> None:
    assert "Balances" in output
    assert "Settlement" in output
    assert re.search(rf"│ {re.escape(sender)}\s+│ {re.escape(recipient)}\s+│\s+{re.escape(amount)} │", output)


def test_settle_csv_file(tmp_path: Path) -> None:
    csv_path = _write_payments_csv(
        tmp_path,
        'amount,payer,members,currency\n300,a,"a,b,c",TWD\n200,b,"b,c",TWD\n',
    )

    result = runner.invoke(app, ["settle", "--file", str(csv_path)])

    assert result.exit_code == 0
    _assert_balance(result.stdout, "a", "-200.00 TWD", "receives")
    _assert_balance(result.stdout, "b", "+0.00 TWD", "settled")
    _assert_balance(result.stdout, "c", "+200.00 TWD", "owes")
    _assert_settlement(result.stdout, "c", "a", "200.00 TWD")


def test_settle_balances_use_display_precision_for_status(tmp_path: Path) -> None:
    csv_path = _write_payments_csv(
        tmp_path,
        'amount,payer,members,currency\n0.008,a,"a,b",TWD\n',
    )

    result = runner.invoke(app, ["settle", "--file", str(csv_path)])

    assert result.exit_code == 0
    _assert_balance(result.stdout, "a", "+0.00 TWD", "settled")
    _assert_balance(result.stdout, "b", "+0.00 TWD", "settled")


def test_settle_csv_file_uses_sheet_csv_parsing(tmp_path: Path) -> None:
    csv_path = _write_payments_csv(
        tmp_path,
        'amount,payer,members,currency\n"1,200",a,"a,b",TWD\n',
    )

    result = runner.invoke(app, ["settle", "--file", str(csv_path)])

    assert result.exit_code == 0
    _assert_settlement(result.stdout, "b", "a", "600.00 TWD")


def test_settle_google_sheet(monkeypatch) -> None:
    calls = {}

    def fake_get(url, **kwargs):
        calls["url"] = url
        calls.update(kwargs)
        return _FakeSheetResponse()

    monkeypatch.setattr(utils.httpx, "get", fake_get)

    result = runner.invoke(app, ["settle", "--sheet", "https://example.test/sheet.csv"])

    assert result.exit_code == 0
    assert calls == {"url": "https://example.test/sheet.csv", "follow_redirects": True, "timeout": 10}
    _assert_settlement(result.stdout, "c", "a", "200.00 TWD")


def test_settle_google_sheet_reports_http_errors(monkeypatch) -> None:
    def fake_get(url, **kwargs):
        request = httpx.Request("GET", url)
        raise httpx.RequestError("network down", request=request)

    monkeypatch.setattr(utils.httpx, "get", fake_get)

    result = runner.invoke(app, ["settle", "--sheet", "https://example.test/sheet.csv"])

    assert result.exit_code != 0
    assert "HTTP request failed: network down" in result.output
    assert "Traceback" not in result.output


def test_settle_requires_exactly_one_source() -> None:
    result = runner.invoke(app, ["settle"])

    assert result.exit_code != 0
    assert "Provide exactly one source" in result.output


def test_settle_reports_missing_csv_columns(tmp_path: Path) -> None:
    csv_path = _write_payments_csv(
        tmp_path,
        "amount,payer,currency\n100,a,TWD\n",
    )

    result = runner.invoke(app, ["settle", "--file", str(csv_path)])

    assert result.exit_code != 0
    assert "Payment CSV missing required columns: members" in result.output


def test_settle_alias_option(tmp_path: Path) -> None:
    csv_path = _write_payments_csv(
        tmp_path,
        'amount,payer,members,currency\n300,a,"a,b,c",TWD\n200,b,"b,c",TWD\n',
    )

    result = runner.invoke(app, ["settle", "--file", str(csv_path), "--alias", "c=a"])

    assert result.exit_code == 0
    assert "Balances" in result.stdout
    _assert_balance(result.stdout, "a", "+0.00 TWD", "settled")
    _assert_balance(result.stdout, "b", "+0.00 TWD", "settled")
    _assert_no_balance(result.stdout, "c")
    assert "No transactions needed." in result.stdout


def test_settle_alias_target_can_be_new_member(tmp_path: Path) -> None:
    csv_path = _write_payments_csv(
        tmp_path,
        'amount,payer,members,currency\n100,b,"b,c",TWD\n',
    )

    result = runner.invoke(app, ["settle", "--file", str(csv_path), "--alias", "c=a"])

    assert result.exit_code == 0
    _assert_balance(result.stdout, "a", "+50.00 TWD", "owes")
    _assert_balance(result.stdout, "b", "-50.00 TWD", "receives")
    _assert_no_balance(result.stdout, "c")
    _assert_settlement(result.stdout, "a", "b", "50.00 TWD")


def test_settle_rejects_invalid_alias(tmp_path: Path) -> None:
    csv_path = _write_payments_csv(
        tmp_path,
        'amount,payer,members,currency\n100,a,"a,b",TWD\n',
    )

    result = runner.invoke(app, ["settle", "--file", str(csv_path), "--alias", "bad-alias"])

    assert result.exit_code != 0
    assert "Alias must use FROM=TO format." in result.output


def test_settle_rejects_alias_with_multiple_equals(tmp_path: Path) -> None:
    csv_path = _write_payments_csv(
        tmp_path,
        'amount,payer,members,currency\n100,a,"a,b",TWD\n',
    )

    result = runner.invoke(app, ["settle", "--file", str(csv_path), "--alias", "a=b=c"])

    assert result.exit_code != 0
    assert "Alias must use FROM=TO format." in result.output


def test_settle_currency_option_is_case_insensitive(tmp_path: Path) -> None:
    csv_path = _write_payments_csv(
        tmp_path,
        'amount,payer,members,currency\n100,a,"a,b",USD\n',
    )

    result = runner.invoke(app, ["settle", "--file", str(csv_path), "--currency", "usd"])

    assert result.exit_code == 0
    _assert_settlement(result.stdout, "b", "a", "50.00 USD")
