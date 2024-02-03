from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from .currency import Currency
from .member import Member


class Payment(BaseModel):
    amount: float
    currency: Currency
    payer: Member
    shared: list[Member]
    time: datetime = Field(default_factory=datetime.now)
