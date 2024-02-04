from sharepay import Project


def main() -> None:
    url = "https://docs.google.com/spreadsheets/d/1fW-WCfRLrqzMnCVUQnGRnRy0PKMkFp4kcihIpHiDgdQ/export?format=csv"

    p = Project.from_google_sheet(url, currency="TWD")
    p.settle_up()


if __name__ == "__main__":
    main()
