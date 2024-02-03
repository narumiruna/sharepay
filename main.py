from sharepay import Currency
from sharepay import Member
from sharepay import Payment
from sharepay import Project


def main() -> None:
    members = Member.from_names(["narumi", "dogiko", "ben", "john"])

    project = Project(name="test", currency=Currency.JPY)

    payments = [
        Payment(
            amount=300,
            currency=Currency.JPY,
            payer=members["narumi"],
            members=[members["narumi"], members["dogiko"], members["ben"]],
        ),
        Payment(
            amount=900,
            currency=Currency.JPY,
            payer=members["dogiko"],
            members=[members["narumi"], members["dogiko"], members["ben"]],
        ),
        Payment(amount=600, currency=Currency.JPY, payer=members["ben"], members=[members["john"], members["john"]]),
    ]

    project.add_payments(payments)

    project.settle_up()


if __name__ == "__main__":
    main()
