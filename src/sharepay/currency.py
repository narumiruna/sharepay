from enum import StrEnum


class Currency(StrEnum):
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    TWD = "TWD"
    USD = "USD"
    CAD = "CAD"

    def __str__(self) -> str:
        return self.value
