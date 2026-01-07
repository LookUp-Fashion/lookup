import json
import re
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup

from app.models.item import PriceSnapshot, Product, SourceSiteType
from app.models.currency_code import CurrencyCode

_STATE_RE = re.compile(r"window\.__MSS__\.product\.state\s*=\s*({.*?});", re.DOTALL)


def _extract_mss_state_from_html(html_content: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_content, "html.parser")

    script_tag = soup.find("script", id="pdp-data")
    if not script_tag or not script_tag.string:
        raise ValueError("pdp-data script not found")

    match = _STATE_RE.search(script_tag.string)
    if not match:
        raise ValueError("window.__MSS__.product.state not found")

    return json.loads(match.group(1))


def parse_musinsa_product(html_content: str, *, url: Optional[str] = None) -> Product:
    data = _extract_mss_state_from_html(html_content)

    source_product_id = data.get("goodsNo")
    if source_product_id is None:
        raise ValueError("goodsNo not found")

    image_urls = []
    for img in data.get("goodsImages", [])[:3]:
        if isinstance(img, dict) and img.get("imageUrl"):
            image_urls.append(img["imageUrl"])

    category_path = []
    category = data.get("category")
    if isinstance(category, dict):
        # best-effort: keep human-readable category names if present
        for key in ("depth1Name", "depth2Name", "depth3Name", "depth4Name"):
            val = category.get(key)
            if val:
                category_path.append(str(val))

    metadata = {
        "style_no": data.get("styleNo"),
        "season": f"{data.get('seasonYear')}-{data.get('season')}",
        "gender": data.get("sex"),
        "material": data.get("goodsMaterial"),
        "stats": data.get("goodsReview"),
        "manufacturer": {
            "name": (data.get("company") or {}).get("name"),
            "business_number": (data.get("company") or {}).get("businessNumber"),
        },
    }

    return Product(
        source=SourceSiteType.MUSINSA,
        source_product_id=str(source_product_id),
        url=url,
        name=data.get("goodsNm"),
        brand=(data.get("brandInfo") or {}).get("brandName"),
        image_urls=image_urls,
        category_path=category_path,
        metadata=metadata,
    )


def parse_musinsa_price(
    html_content: str, *, url: Optional[str] = None
) -> PriceSnapshot:
    data = _extract_mss_state_from_html(html_content)

    source_product_id = data.get("goodsNo")
    if source_product_id is None:
        raise ValueError("goodsNo not found")

    goods_price = data.get("goodsPrice") or {}
    original = goods_price.get("normalPrice")
    sale = goods_price.get("salePrice")
    discount_rate = goods_price.get("discountRate")

    return PriceSnapshot(
        source=SourceSiteType.MUSINSA,
        source_product_id=str(source_product_id),
        url=url,
        currency=CurrencyCode.KRW,
        original=original,
        sale=sale,
        discount_rate=discount_rate,
    )
