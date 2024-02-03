from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class Member(BaseModel):
    name: str
    balance: float = Field(default=0)

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        return v.lower().strip()

    @classmethod
    def from_names(cls, names: list[str]) -> dict[str, "Member"]:
        d = {}
        for name in names:
            name = name.lower().strip()
            d[name] = cls(name=name)
        return d
