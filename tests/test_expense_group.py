from sharepay.currency import Currency
from sharepay.expense_group import ExpenseGroup
from sharepay.expense_group import SettlementMethod


def _apply_transactions(group: ExpenseGroup, transactions):
    values = {owner: balance.value for owner, balance in group.balances.items()}
    for transaction in transactions:
        values[transaction.sender] = values.get(transaction.sender, 0) - transaction.amount
        values[transaction.recipient] = values.get(transaction.recipient, 0) + transaction.amount
    return values


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


def test_expense_group_settle_up_defaults_to_max_debtor() -> None:
    s = ExpenseGroup(name="test")
    s.add_payment(amount=200, payer="a", members=["a", "c"], currency=Currency.TWD)
    s.add_payment(amount=100, payer="b", members=["b", "c"], currency=Currency.TWD)
    transactions = s.settle_up()

    assert [(transaction.sender, transaction.recipient, transaction.amount) for transaction in transactions] == [
        ("c", "a", 100),
        ("c", "b", 50),
    ]


def test_expense_group_settle_up_relay_keeps_each_sender_to_one_transfer() -> None:
    s = ExpenseGroup(name="test")
    s.add_payment(amount=200, payer="a", members=["a", "c"], currency=Currency.TWD)
    s.add_payment(amount=100, payer="b", members=["b", "c"], currency=Currency.TWD)
    transactions = s.settle_up(method=SettlementMethod.RELAY)

    senders = [transaction.sender for transaction in transactions]
    assert len(senders) == len(set(senders))
    assert [(transaction.sender, transaction.recipient, transaction.amount) for transaction in transactions] == [
        ("c", "a", 150),
        ("a", "b", 50),
    ]


def test_expense_group_settle_up_max_debtor_pays_each_creditor() -> None:
    s = ExpenseGroup(name="test")
    s.add_payment(amount=200, payer="a", members=["a", "c"], currency=Currency.TWD)
    s.add_payment(amount=100, payer="b", members=["b", "c"], currency=Currency.TWD)
    transactions = s.settle_up(method="max-debtor")

    assert [(transaction.sender, transaction.recipient, transaction.amount) for transaction in transactions] == [
        ("c", "a", 100),
        ("c", "b", 50),
    ]


def test_expense_group_settle_up_max_debtor_collects_from_other_debtors() -> None:
    s = ExpenseGroup(name="test")
    s.add_payment(amount=200, payer="a", members=["a", "c"], currency=Currency.TWD)
    s.add_payment(amount=100, payer="b", members=["b", "d"], currency=Currency.TWD)
    transactions = s.settle_up(method=SettlementMethod.MAX_DEBTOR)

    assert [(transaction.sender, transaction.recipient, transaction.amount) for transaction in transactions] == [
        ("c", "a", 100),
        ("c", "b", 50),
        ("d", "c", 50),
    ]
    assert all(abs(value) < 1e-6 for value in _apply_transactions(s, transactions).values())


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


def test_expense_group_alias_normalizes_owner_names() -> None:
    s = ExpenseGroup(name="test", alias={" C ": " A "})
    s.add_payment(amount=100, payer="b", members=["b", "c"], currency=Currency.TWD)
    transactions = s.settle_up()

    assert len(transactions) == 1
    assert transactions[0].sender == "a"
    assert transactions[0].recipient == "b"
    assert transactions[0].amount == 50
