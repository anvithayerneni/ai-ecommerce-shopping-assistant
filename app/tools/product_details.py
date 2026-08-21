from langchain_core.tools import tool

from app.db.session import SessionLocal
from app.models.product import Product


@tool
def get_product_details(product_id: int) -> dict | None:
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

    finally:
        db.close()
