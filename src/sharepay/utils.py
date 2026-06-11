import io
import json
from pathlib import Path

import httpx
import pandas as pd

PAYMENT_COLUMNS = ["payer", "members", "amount", "currency"]


def save_json(obj: object, f: str) -> None:
    with Path(f).open("w") as fp:
        json.dump(obj, fp, indent=4, ensure_ascii=False)


def _payment_columns(df: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [column for column in PAYMENT_COLUMNS if column not in df.columns]
    if missing_columns:
        columns = ", ".join(missing_columns)
        msg = f"Payment CSV missing required columns: {columns}"
        raise ValueError(msg)

    return df[PAYMENT_COLUMNS]


def read_payment_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(
        str(path),
        dtype={"amount": float, "currency": str, "payer": str, "members": str},
        thousands=",",
    )
    return _payment_columns(df)


def read_google_sheet(url: str) -> pd.DataFrame:
    resp = httpx.get(url, follow_redirects=True, timeout=10)
    resp.raise_for_status()
    df = pd.read_csv(
        io.BytesIO(resp.content),
        dtype={"amount": float, "currency": str, "payer": str, "members": str},
        thousands=",",
    )
    return _payment_columns(df)
