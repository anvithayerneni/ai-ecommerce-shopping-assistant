from __future__ import annotations

from langchain_core.tools import tool

from app.db.session import SessionLocal
from app.models.product import Product


def _product_to_dict(product: Product) -> dict:
    """
    Convert a Product ORM object into the application's
    standard product dictionary.
    """

    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "subcategory": product.subcategory,
        "price": product.price,
        "rating": product.rating,
        "stock": product.stock,
        "tags": product.tags,
        "features": product.features,
        "target_audience": product.target_audience,
        "use_cases": product.use_cases,
    }


@tool
def get_product_details(
    product_id: int,
) -> dict | None:
    """
    Retrieve detailed information about a single product
    from the product database.
    """

    db = SessionLocal()

    try:
        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            return None

        return _product_to_dict(product)

    finally:
        db.close()


def find_product_by_name(
    product_name: str,
) -> dict | None:
    """
    Resolve a product name to an authoritative catalog product.

    This is deterministic database lookup.
    It does not use an LLM.

    Matching order:
        1. Exact case-insensitive name match
        2. Partial case-insensitive name match

    Returns None when no product can be resolved.
    """

    name = product_name.strip()

    if not name:
        return None

    db = SessionLocal()

    try:
        # ----------------------------------------------------
        # Exact match
        # ----------------------------------------------------

        product = (
            db.query(Product)
            .filter(
                Product.name.ilike(name)
            )
            .first()
        )

        if product:
            return _product_to_dict(product)

        # ----------------------------------------------------
        # Partial match
        # ----------------------------------------------------

        product = (
            db.query(Product)
            .filter(
                Product.name.ilike(
                    f"%{name}%"
                )
            )
            .first()
        )

        if product:
            return _product_to_dict(product)

        return None

    finally:
        db.close()