import io

import pandas as pd
import requests


def read_csv_from_google_sheet(url: str) -> pd.DataFrame:
    resp = requests.get(url)
    df = pd.read_csv(io.BytesIO(resp.content))
    df.fillna("", inplace=True)
    return df


def parse_name(s: str) -> str:
    s = s.strip().lower()

    if s == "":
        msg = f"invalid name: {s}"
        raise ValueError(msg)

    return s


def parse_float(v: str | float) -> float:
    if isinstance(v, float):
        return v

    if v == "":
        return 0
    return float(v.replace(",", ""))


def parse_currency(s: str) -> str:
    return s.strip().upper()


def parse_names(raw: str) -> list[str]:
    res = []

    if raw == "":
        raise ValueError("empty string")

    for s in raw.split(","):
        res += [parse_name(s)]

    return res
