from dataclasses import dataclass
from typing import Optional

from app.models.currency_code import CurrencyCode
from app.models.type import SourceSiteType


@dataclass(frozen=True)
class PriceSnapshot:
    source: SourceSiteType
    source_product_id: str
    url: Optional[str] = None

    currency: CurrencyCode = CurrencyCode.KRW
    original: Optional[int] = None
    sale: Optional[int] = None
    discount_rate: Optional[float] = None
