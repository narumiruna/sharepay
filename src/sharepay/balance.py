from __future__ import annotations

import uuid

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator

from .currency import Currency


class Balance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner: str
    value: float = Field(default=0)
    currency: Currency = Field(default=Currency.TWD)

    @field_validator("owner")
    @classmethod
    def validate_owner(cls, v: str) -> str:
        return v.lower().strip()
