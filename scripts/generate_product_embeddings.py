import json
from pathlib import Path

from app.db.session import SessionLocal
from app.models.product import Product
from app.services.embedding_service import embedding_service


OUTPUT_FILE = Path("data/product_embeddings.json")


def generate_product_embeddings() -> None:
    db = SessionLocal()

    try:
        products = (
            db.query(Product)
            .filter(Product.search_text.is_not(None))
            .order_by(Product.id)
            .all()
        )

        embeddings = []

        for product in products:
            vector = embedding_service.embed_text(product.search_text)

            embeddings.append(
                {
                    "product_id": product.id,
                    "name": product.name,
                    "embedding": vector,
                }
            )

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                embeddings,
                file,
                indent=2,
            )

        print(
            f"Generated embeddings for {len(embeddings)} products."
        )
        print(f"Saved embeddings to {OUTPUT_FILE}")

    finally:
        db.close()


if __name__ == "__main__":
    generate_product_embeddings()