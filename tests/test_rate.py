from datetime import datetime

from sharepay.rate import Rate
from sharepay.rate import query_rate


def test_rate_init() -> None:
    source = "TWD"
    target = "JPY"
    value = 0.2
    t = 1704067200000
    r = Rate(source=source, target=target, value=value, time=t)

    assert r.source == source
    assert r.target == target
    assert r.value == value
    assert r.time == datetime.fromtimestamp(t // 1000)


def test_query_rate() -> None:
    assert query_rate("TWD", "JPY") > 0
    assert query_rate("TWD", "JPY") > 0

    assert query_rate("TWD", "TWD") == 1
