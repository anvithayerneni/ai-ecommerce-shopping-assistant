from __future__ import annotations

from typing import Any


def filter_products(
    products: list[dict[str, Any]],
    *,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    use_case: str | None = None,
) -> list[dict[str, Any]]:
    """
    Filter products using structured shopping constraints.

    This tool performs deterministic filtering only.
    It does not use an LLM.
    """

    filtered: list[dict[str, Any]] = []

    for product in products:
        # ----------------------------------------------------
        # Category
        # ----------------------------------------------------

        if category:
            product_category = str(
                product.get("category") or ""
            ).lower()

            if category.lower() not in product_category:
                continue

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        price = product.get("price")

        if price is None:
            continue

        try:
            price = float(price)
        except (TypeError, ValueError):
            continue

        if min_price is not None and price < min_price:
            continue

        if max_price is not None and price > max_price:
            continue

        # ----------------------------------------------------
        # Rating
        # ----------------------------------------------------

        if min_rating is not None:
            rating = product.get("rating")

            if rating is None:
                continue

            try:
                rating = float(rating)
            except (TypeError, ValueError):
                continue

            if rating < min_rating:
                continue

        # ----------------------------------------------------
        # Use case
        # ----------------------------------------------------

        if use_case:
            product_use_cases = str(
                product.get("use_cases") or ""
            ).lower()

            if use_case.lower() not in product_use_cases:
                continue

        filtered.append(product)

    return filtered
