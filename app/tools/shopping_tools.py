from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from app.services.search_service import search_products
from app.tools.product_compare import compare_products
from app.tools.product_details import get_product_details
from app.tools.product_filter import filter_products


# ============================================================
# SEARCH CATALOG
# ============================================================

@tool
def search_catalog(
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Search the product catalog for products relevant to a
    natural-language shopping query.
    """

    return search_products(
        query=query,
        top_k=top_k,
    )


# ============================================================
# FILTER CATALOG
# ============================================================

@tool
def filter_catalog(
    products: list[dict[str, Any]],
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    use_case: str | None = None,
) -> list[dict[str, Any]]:
    """
    Apply deterministic filters to a list of products.

    Filters include:
    - category
    - minimum price
    - maximum price
    - minimum rating
    - use case
    """

    return filter_products(
        products,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        use_case=use_case,
    )


# ============================================================
# GET PRODUCT
# ============================================================

@tool
def get_product(
    product_id: int | str,
) -> dict[str, Any]:
    """
    Retrieve detailed information about a specific product.
    """

    return get_product_details.invoke(
        {
            "product_id": product_id,
        }
    )


# ============================================================
# COMPARE PRODUCTS
# ============================================================

@tool
def compare_catalog_products(
    product_ids: list[int | str],
) -> dict[str, Any]:
    """
    Compare specific products using authoritative catalog data.

    The caller provides product IDs.

    This tool retrieves each product directly from the catalog
    before performing the deterministic comparison.

    It does not allow the LLM to supply or modify product
    attributes such as price, rating, features, or use cases.
    """

    if not product_ids:
        return {
            "products": [],
            "comparison": [],
            "cheapest": None,
            "highest_rated": None,
            "use_case_comparison": {},
            "grounding_rules": [
                "No product IDs were provided."
            ],
        }

    products: list[dict[str, Any]] = []

    for product_id in product_ids:

        try:
            product = get_product_details.invoke(
                {
                    "product_id": product_id,
                }
            )

        except Exception as exc:

            products.append(
                {
                    "id": product_id,
                    "error": (
                        f"Unable to retrieve product: {exc}"
                    ),
                }
            )

            continue

        if product:
            products.append(
                product
            )

    # --------------------------------------------------------
    # Remove products that could not be retrieved
    # --------------------------------------------------------

    valid_products = [
        product
        for product in products
        if not product.get("error")
    ]

    # --------------------------------------------------------
    # Deterministic comparison
    # --------------------------------------------------------

    return compare_products(
        valid_products
    )


# ============================================================
# TOOL COLLECTION
# ============================================================

SHOPPING_TOOLS = [
    search_catalog,
    filter_catalog,
    get_product,
    compare_catalog_products,
]