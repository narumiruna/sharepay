from sharepay import Currency
from sharepay import Member
from sharepay import Payment
from sharepay import Project


def main() -> None:
    members = Member.from_names(["narumi", "dogiko", "ben", "john"])

    project = Project(name="test", members=list(members.values()))

    project.add_payment(
        Payment(
            amount=300,
            currency=Currency.JPY,
            payer=members["narumi"],
            members=[members["narumi"], members["dogiko"], members["ben"]],
        )
    )
    project.add_payment(
        Payment(
            amount=900,
            currency=Currency.JPY,
            payer=members["dogiko"],
            members=[members["narumi"], members["dogiko"], members["ben"]],
        )
    )
    project.add_payment(
        Payment(amount=600, currency=Currency.JPY, payer=members["ben"], members=[members["john"], members["john"]])
    )

    for d in project.debts:
        print(d)

    x = 0
    for _, m in members.items():
        x += m.balance
        print(m)
    assert x == 0

    project.settle_up()


if __name__ == "__main__":
    main()
