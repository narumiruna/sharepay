from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from .currency import Currency


class Balance(BaseModel):
    owner: str
    value: float = Field(default=0)
    currency: Currency = Field(default=Currency.TWD)

    @field_validator("owner")
    @classmethod
    def validate_owner(cls, v: str) -> str:
        return v.lower().strip()
