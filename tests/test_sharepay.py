from sharepay.currency import Currency
from sharepay.sharepay import SharePay


def test_sharepay():
    s = SharePay(name="test")
    s.add_payment(amount=300, payer_name="a", member_names=["a", "b", "c"], currency=Currency.TWD)
    s.add_payment(amount=200, payer_name="b", member_names=["b", "c"], currency=Currency.TWD)
    s.settle_up()

    assert s.members["a"].balance == 300 * 2 / 3
    assert s.members["b"].balance == -300 / 3 + 200 / 2
    assert s.members["c"].balance == -300 / 3 - 200 / 2
