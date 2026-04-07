from sharepay.currency import Currency
from sharepay.expense_group import ExpenseGroup


def test_expense_group_currency() -> None:
    s = ExpenseGroup(name="test", currency=Currency.TWD)
    s.add_payment(amount=300, payer="a", members=["a", "b", "c"], currency=Currency.JPY)
    s.settle_up()

    assert s.currency == Currency.TWD
    assert s.payments[0].currency == Currency.JPY

    assert s.balances["a"].value != -300 * 2 / 3
    assert s.balances["b"].value == s.balances["b"].value


def test_expense_group_balance() -> None:
    s = ExpenseGroup(name="test")
    s.add_payment(amount=300, payer="a", members=["a", "b", "c"], currency=Currency.TWD)
    s.add_payment(amount=200, payer="b", members=["b", "c"], currency=Currency.TWD)
    s.settle_up()

    assert s.balances["a"].value == -300 * 2 / 3
    assert s.balances["b"].value == 300 / 3 - 200 / 2
    assert s.balances["c"].value == 300 / 3 + 200 / 2

    assert sum([m.value for m in s.balances.values()]) == 0


def test_expense_group_settle_up() -> None:
    s = ExpenseGroup(name="test")
    s.add_payment(amount=300, payer="a", members=["a", "b", "c"], currency=Currency.TWD)
    s.add_payment(amount=200, payer="b", members=["b", "c"], currency=Currency.TWD)
    transactions = s.settle_up()

    assert len(transactions) == 1
    assert transactions[0].sender == "c"
    assert transactions[0].recipient == "a"
    assert transactions[0].amount == 200


def test_expense_group_alias() -> None:
    s = ExpenseGroup(name="test", alias={"c": "a"})
    s.add_payment(amount=300, payer="a", members=["a", "b", "c"], currency=Currency.TWD)
    s.add_payment(amount=200, payer="b", members=["b", "c"], currency=Currency.TWD)
    transactions = s.settle_up()

    print(transactions)
    assert len(transactions) == 0
    assert s.balances["a"].value == 0
    assert s.balances["b"].value == 0
    assert s.balances["c"].value == 0
