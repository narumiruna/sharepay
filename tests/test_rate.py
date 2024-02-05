from sharepay.rate import query_rate


def test_query_rate():
    assert query_rate("JPY", "TWD") > 0
    assert query_rate("TWD", "JPY") > 0
    assert query_rate("TWD", "JPY") > 0
    assert query_rate("TWD", "TWD") == 1
