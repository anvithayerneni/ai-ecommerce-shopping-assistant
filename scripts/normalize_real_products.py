import re
from typing import Any


PRICE_PATTERN = re.compile(
    r"\$\s?(\d+(?:,\d{3})*(?:\.\d{2})?)"
)


def extract_price(text: str) -> float | None:
    match = PRICE_PATTERN.search(text)

    if not match:
        return None

    price = match.group(1).replace(",", "")

    return float(price)


def normalize_product(product: dict[str, Any]) -> dict[str, Any]:
    vendor = product.get("vendor", "").strip()
    title = product.get("title", "").strip()
    paragraph = product.get("paragraph", "").strip()

    return {
        "external_id": product.get("uid"),
        "name": title,
        "description": paragraph,
        "brand": vendor,
        "price": extract_price(paragraph),
        "source_embedding": product.get("embedding"),
    }