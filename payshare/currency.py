from enum import Enum


class Currency(str, Enum):
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    TWD = "TWD"
    USD = "USD"
