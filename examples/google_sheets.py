from sharepay.currency import Currency
from sharepay.sharepay import SharePay


def main() -> None:
    url = "https://docs.google.com/spreadsheets/d/1fW-WCfRLrqzMnCVUQnGRnRy0PKMkFp4kcihIpHiDgdQ/export?format=csv"

    p = SharePay.from_sheet(url, currency=Currency.TWD)
    transaction = p.settle_up()
    for t in transaction:
        print(t)


if __name__ == "__main__":
    main()
