from sharepay.currency import Currency
from sharepay.sharepay import SharePay


def main() -> None:
    url = "https://docs.google.com/spreadsheets/d/1fW-WCfRLrqzMnCVUQnGRnRy0PKMkFp4kcihIpHiDgdQ/export?format=csv"

    p = SharePay.from_sheet(url, currency=Currency.TWD)
    p.settle_up()


if __name__ == "__main__":
    main()
