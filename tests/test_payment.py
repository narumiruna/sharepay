from datetime import datetime

from sharepay.currency import Currency
from sharepay.member import Member
from sharepay.payment import Payment


def test_payment_validate_time() -> None:
    a = 100
    c = Currency.TWD
    m = Member(name="test")
    dt = datetime(year=2024, month=1, day=1)

    p = Payment(amount=a, currency=c, payer=m, members=[], time=dt.strftime("%Y-%m-%d"))
    assert p.time == dt

    p = Payment(amount=a, currency=c, payer=m, members=[], time=dt)
    assert p.time == dt
