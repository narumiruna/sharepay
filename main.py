from sharepay import Currency
from sharepay import Project


def main() -> None:
    project = Project(name="test", currency=Currency.JPY, alias={"cindy": "john"})

    project.create_payment(amount=300, currency="JPY", payer_name="narumi", member_names=["narumi", "dogiko", "ben"])
    project.create_payment(amount=900, currency="JPY", payer_name="dogiko", member_names=["narumi", "dogiko", "ben"])
    project.create_payment(amount=600, currency="JPY", payer_name="ben", member_names=["john", "cindy"])

    project.settle_up()


if __name__ == "__main__":
    main()
