import io
import json

import pandas as pd
import requests


def save_json(obj, f) -> None:
    with open(f, "w") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)


def read_csv_from_google_sheet(url: str) -> pd.DataFrame:
    df = pd.read_csv(
        io.BytesIO(requests.get(url).content),
        dtype={"amount": float, "currency": str, "payer": str, "members": str},
        thousands=",",
    )
    return df[["payer", "members", "amount", "currency"]]
