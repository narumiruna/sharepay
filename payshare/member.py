from pydantic import BaseModel


class Member(BaseModel):
    name: str
