import io
import json
from pathlib import Path
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlparse

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


def _extract_gid(value: str) -> str | None:
    gids = parse_qs(value).get("gid")
    if not gids:
        return None

    return gids[0]


def _google_sheet_csv_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc != "docs.google.com":
        return url

    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 3 or path_parts[:2] != ["spreadsheets", "d"]:
        return url

    if "export" in path_parts or path_parts[-2:] == ["gviz", "tq"]:
        return url

    query = {"format": "csv"}
    gid = _extract_gid(parsed.query) or _extract_gid(parsed.fragment)
    if gid is not None:
        query["gid"] = gid

    spreadsheet_id = path_parts[2]
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?{urlencode(query)}"


def read_google_sheet(url: str) -> pd.DataFrame:
    resp = httpx.get(_google_sheet_csv_url(url), follow_redirects=True, timeout=10)
    resp.raise_for_status()
    df = pd.read_csv(
        io.BytesIO(resp.content),
        dtype={"amount": float, "currency": str, "payer": str, "members": str},
        thousands=",",
    )
    return _payment_columns(df)
