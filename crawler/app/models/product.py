from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.models.type import SourceSiteType


@dataclass(frozen=True)
class Product:
    source: SourceSiteType
    source_product_id: str
    url: Optional[str] = None

    name: Optional[str] = None
    brand: Optional[str] = None

    image_urls: List[str] = field(default_factory=list)
    category_path: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)
