from sharepay import utils


class _FakeResponse:
    content = b'amount,payer,members,currency\n100,a,"a,b",TWD\n'

    def __init__(self) -> None:
        self.raise_for_status_called = False

    def raise_for_status(self) -> None:
        self.raise_for_status_called = True


def test_read_google_sheet_uses_timeout_and_checks_status(monkeypatch) -> None:
    response = _FakeResponse()
    calls = {}

    def fake_get(url, **kwargs):
        calls["url"] = url
        calls.update(kwargs)
        return response

    monkeypatch.setattr(utils.httpx, "get", fake_get)

    df = utils.read_google_sheet("https://example.test/sheet.csv")

    assert calls == {"url": "https://example.test/sheet.csv", "follow_redirects": True, "timeout": 10}
    assert response.raise_for_status_called
    assert df.to_dict("records") == [{"payer": "a", "members": "a,b", "amount": 100.0, "currency": "TWD"}]
