from sharepay.currency import Currency
from sharepay.sharepay import SharePay


def test_sharepay_currency() -> None:
    s = SharePay(name="test", currency=Currency.TWD)
    s.add_payment(amount=300, payer_name="a", member_names=["a", "b", "c"], currency=Currency.JPY)
    s.settle_up()

    assert s.currency == Currency.TWD
    assert s.payments[0].currency == Currency.JPY

    assert s.members["a"].balance != 300 * 2 / 3
    assert s.members["b"].balance == s.members["b"].balance


def test_sharepay_balance() -> None:
    s = SharePay(name="test")
    s.add_payment(amount=300, payer_name="a", member_names=["a", "b", "c"], currency=Currency.TWD)
    s.add_payment(amount=200, payer_name="b", member_names=["b", "c"], currency=Currency.TWD)
    s.settle_up()

    assert s.members["a"].balance == 300 * 2 / 3
    assert s.members["b"].balance == -300 / 3 + 200 / 2
    assert s.members["c"].balance == -300 / 3 - 200 / 2

    assert sum([m.balance for m in s.members.values()]) == 0


def test_sharepay_settle_up() -> None:
    s = SharePay(name="test")
    s.add_payment(amount=300, payer_name="a", member_names=["a", "b", "c"], currency=Currency.TWD)
    s.add_payment(amount=200, payer_name="b", member_names=["b", "c"], currency=Currency.TWD)
    transactions = s.settle_up()

    assert len(transactions) == 1
    assert transactions[0].sender.name == "c"
    assert transactions[0].recipient.name == "a"
    assert transactions[0].amount == 200


def test_sharepay_alias() -> None:
    s = SharePay(name="test", alias={"c": "a"})
    s.add_payment(amount=300, payer_name="a", member_names=["a", "b", "c"], currency=Currency.TWD)
    s.add_payment(amount=200, payer_name="b", member_names=["b", "c"], currency=Currency.TWD)
    transactions = s.settle_up()

    assert len(transactions) == 0
    assert s.members["a"].balance == 0
    assert s.members["b"].balance == 0
    assert s.members["c"].balance == 0
