from sharepay import Currency
from sharepay import SharePay


def main() -> None:
    project = SharePay(name="Sendai", currency=Currency.TWD, alias={"yoan": "john"})

    project.add_payment(amount=300, currency="JPY", payer_name="narumi", member_names=["narumi", "dogiko", "ben"])
    project.add_payment(amount=600, currency="JPY", payer_name="dogiko", member_names=["dogiko", "ben", "john"])
    project.add_payment(amount=900, currency="JPY", payer_name="ben", member_names=["john", "yoan"])

    project.settle_up()


if __name__ == "__main__":
    main()
