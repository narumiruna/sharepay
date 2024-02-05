from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class Member(BaseModel):
    name: str
    balance: float = Field(default=0)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        return v.lower().strip()
