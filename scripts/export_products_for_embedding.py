import json
from pathlib import Path

from app.db.session import SessionLocal
from app.models.product import Product


OUTPUT_FILE = Path("data/products_for_embedding.json")


def export_products() -> None:
    db = SessionLocal()

    try:
        products = db.query(Product).order_by(Product.id).all()

        documents = []

        for product in products:
            documents.append(
                {
                    "product_id": product.id,
                    "name": product.name,
                    "search_text": product.search_text,
                    "category": product.category,
                    "subcategory": product.subcategory,
                    "brand": product.brand,
                    "price": product.price,
                    "rating": product.rating,
                }
            )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(documents, file, indent=2, ensure_ascii=False)

        print(f"Exported {len(documents)} products to {OUTPUT_FILE}")

    finally:
        db.close()


if __name__ == "__main__":
    export_products()