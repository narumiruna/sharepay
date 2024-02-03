from sharepay import Project
from sharepay.utils import read_csv_from_google_sheet


def main() -> None:
    url = "https://docs.google.com/spreadsheets/d/1fW-WCfRLrqzMnCVUQnGRnRy0PKMkFp4kcihIpHiDgdQ/export?format=csv"

    df = read_csv_from_google_sheet(url)
    p = Project.from_df(df)
    p.settle_up()


if __name__ == "__main__":
    main()
