from pydantic import BaseModel

from .currency import Currency


class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float
    currency: Currency

    def __str__(self) -> str:
        return f"{self.sender: <6} -> {self.recipient: <6} {self.amount: >10.2f} {self.currency}"
