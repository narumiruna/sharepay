import io

import pandas as pd
import requests


def read_csv_from_google_sheet(url: str) -> pd.DataFrame:
    resp = requests.get(url)
    df = pd.read_csv(io.BytesIO(resp.content))
    df.fillna("", inplace=True)
    return df


def parse_name(df: pd.DataFrame) -> list[str]:
    names = set()

    for row in df["creditor"].astype(str):
        for s in row.split(","):
            names.add(s.lower().strip())

    for row in df["debator"].astype(str):
        for s in row.split(","):
            names.add(s.lower().strip())

    return list(names)
