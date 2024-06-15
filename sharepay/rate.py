from __future__ import annotations

from datetime import datetime

import requests
from pydantic import BaseModel
from pydantic import field_validator
from requests.utils import default_headers

DEFAULT_TIMEOUT = 10
STORE: dict[str, float] = {}


class Rate(BaseModel):
    source: str
    target: str
    value: float
    time: datetime

    @field_validator("time", mode="before")
    @classmethod
    def convert_int(cls, v: datetime | int) -> datetime:
        if isinstance(v, int):
            return datetime.fromtimestamp(v // 1000)

        return v


class RateRequest(BaseModel):
    source: str
    target: str

    def do(self) -> Rate:
        resp = requests.get(
            "https://wise.com/rates/live",
            params=self.model_dump(),
            headers=default_headers(),
            timeout=DEFAULT_TIMEOUT,
        )
        return Rate(**resp.json())


def query_rate(source: str, target: str) -> float:
    source = source.upper()
    target = target.upper()

    if source == target:
        return 1.0

    symbol = f"{source}/{target}"
    if symbol in STORE:
        return STORE[symbol]

    rate = RateRequest(source=source, target=target).do()
    STORE[symbol] = rate.value
    return rate.value
