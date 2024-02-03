from payshare import Currency
from payshare import Member
from payshare import Payment
from payshare import settle_up


def main() -> None:
    members = Member.from_names(["narumi", "dogiko", "ben", "john"])

    debts = []
    debts += Payment(
        amount=300,
        currency=Currency.JPY,
        payer=members["narumi"],
        members=[members["narumi"], members["dogiko"], members["ben"]],
    ).debts()
    debts += Payment(
        amount=900,
        currency=Currency.JPY,
        payer=members["dogiko"],
        members=[members["narumi"], members["dogiko"], members["ben"]],
    ).debts()
    debts += Payment(
        amount=600, currency=Currency.JPY, payer=members["ben"], members=[members["john"], members["john"]]
    ).debts()

    for d in debts:
        print(d)

    x = 0
    for _, m in members.items():
        x += m.balance
        print(m)
    assert x == 0

    settle_up(list(members.values()))


if __name__ == "__main__":
    main()
