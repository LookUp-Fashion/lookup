from enum import Enum, unique


@unique
class CurrencyCode(str, Enum):
    KRW = "KRW"
