from pydantic import BaseModel

from .currency import Currency
from .member import Member


class Transaction(BaseModel):
    sender: Member
    recipient: Member
    amount: float
    currency: Currency

    def __str__(self) -> str:
        return f"{self.sender.name: <6} -> {self.recipient.name: <6} {self.amount: >10.2f} {self.currency}"
