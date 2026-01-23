import io
import json
from pathlib import Path

import httpx
import pandas as pd


def save_json(obj: object, f: str) -> None:
    with Path(f).open("w") as fp:
        json.dump(obj, fp, indent=4, ensure_ascii=False)


def read_google_sheet(url: str) -> pd.DataFrame:
    df = pd.read_csv(
        io.BytesIO(httpx.get(url, follow_redirects=True).content),
        dtype={"amount": float, "currency": str, "payer": str, "members": str},
        thousands=",",
    )
    return df[["payer", "members", "amount", "currency"]]
