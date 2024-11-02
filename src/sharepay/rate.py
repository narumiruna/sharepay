from __future__ import annotations

from datetime import datetime
from functools import cache

import httpx
from loguru import logger
from pydantic import BaseModel
from pydantic import field_validator


class Rate(BaseModel):
    source: str
    target: str
    value: float
    time: datetime | int

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
        resp = httpx.get(
            "https://wise.com/rates/live",
            params=self.model_dump(),
            timeout=10,
        )
        resp.raise_for_status()
        return Rate.model_validate(resp.json())


@cache
def query_rate(source: str, target: str) -> float:
    source = source.upper()
    target = target.upper()

    if source == target:
        return 1.0

    rate = RateRequest(source=source, target=target).do()
    logger.info("{}/{}: {}", source, target, rate.value)
    return rate.value
