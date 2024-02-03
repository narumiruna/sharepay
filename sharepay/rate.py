from __future__ import annotations

from datetime import datetime

import requests
from pydantic import BaseModel
from pydantic import field_validator
from requests.utils import default_headers

_default_timeout = 10
_store = {}


class Rate(BaseModel):
    source: str
    target: str
    value: float
    time: datetime

    @field_validator("time")
    def validate_time(cls, v) -> datetime:
        if isinstance(v, datetime):
            return v
        elif isinstance(v, int):
            return datetime.fromtimestamp(v // 1000)
        else:
            raise ValueError(f"invalid time: {v}")


class RateRequest(BaseModel):
    source: str
    target: str

    def do(self) -> Rate:
        resp = requests.get(
            "https://wise.com/rates/live",
            params=self.model_dump(),
            headers=default_headers(),
            timeout=_default_timeout,
        )
        return Rate(**resp.json())


def query_rate(source: str, target: str) -> float:
    symbol = f"{source}/{target}"
    if symbol in _store:
        return _store[symbol]

    rate = RateRequest(source=source, target=target).do()
    _store[symbol] = rate.value
    return rate.value
