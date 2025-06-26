from sharepay.currency import Currency
from sharepay.sharepay import SharePay


def main() -> None:
    p = SharePay(name="Sendai", currency=Currency.JPY, alias={"yoan": "john"})

    p.add_payment(amount=300, currency=Currency.JPY, payer="narumi", members=["narumi", "dogiko", "ben"])
    p.add_payment(amount=600, currency=Currency.JPY, payer="dogiko", members=["dogiko", "ben", "john"])
    p.add_payment(amount=900, currency=Currency.JPY, payer="ben", members=["john", "yoan"])

    p.settle_up()


if __name__ == "__main__":
    main()
