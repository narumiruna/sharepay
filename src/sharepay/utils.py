import io
import json

import httpx
import pandas as pd


def save_json(obj, f) -> None:
    with open(f, "w") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)


def read_google_sheet(url: str) -> pd.DataFrame:
    df = pd.read_csv(
        io.BytesIO(httpx.get(url).content),
        dtype={"amount": float, "currency": str, "payer": str, "members": str},
        thousands=",",
    )
    return df[["payer", "members", "amount", "currency"]]
