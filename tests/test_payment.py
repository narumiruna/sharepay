from datetime import datetime

from sharepay.currency import Currency
from sharepay.member import Member
from sharepay.payment import Payment


def test_payment_init() -> None:
    a = Member(name="a")
    b = Member(name="b")
    c = Member(name="c")
    p = Payment(amount=300, currency=Currency.TWD, payer=a, members=[a, b, c], time="2024-01-01")

    assert p.amount == 300
    assert p.currency == Currency.TWD
    assert p.payer == a
    assert p.members == [a, b, c]
    assert p.time == datetime(year=2024, month=1, day=1)
