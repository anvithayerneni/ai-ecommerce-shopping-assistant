from datasets import load_dataset
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.product import Product
from app.services.product_service import build_search_text
from scripts.normalize_real_products import normalize_product


DATASET_NAME = "Tokuhn/TSMPD-US-Public-v1_1"
MAX_PRODUCTS = 1000
BATCH_SIZE = 100


def import_products(
    db: Session,
    max_products: int = MAX_PRODUCTS,
) -> tuple[int, int]:
    dataset = load_dataset(
        DATASET_NAME,
        split="train",
        streaming=True,
    )

    imported = 0
    skipped = 0
    batch: list[Product] = []

    for raw_product in dataset:
        normalized = normalize_product(raw_product)

        external_id = normalized["external_id"]
        price = normalized["price"]

        # Required fields for our current Product model.
        if not external_id or not normalized["name"] or price is None:
            skipped += 1
            continue

        # Prevent duplicate imports.
        existing = (
            db.query(Product.id)
            .filter(Product.external_id == external_id)
            .first()
        )

        if existing:
            skipped += 1
            continue

        product = Product(
            external_id=external_id,
            name=normalized["name"],
            description=normalized["description"],
            brand=normalized["brand"],
            price=price,
            stock=0,
        )

        product.search_text = build_search_text(product)

        batch.append(product)

        if len(batch) >= BATCH_SIZE:
            db.add_all(batch)
            db.commit()

            imported += len(batch)
            batch.clear()

            print(
                f"Imported: {imported} | Skipped: {skipped}"
            )

        if imported >= max_products:
            break

    if batch:
        db.add_all(batch)
        db.commit()

        imported += len(batch)

    return imported, skipped


def main() -> None:
    db = SessionLocal()

    try:
        imported, skipped = import_products(db)

        print()
        print("Import complete.")
        print(f"Imported: {imported}")
        print(f"Skipped: {skipped}")

    finally:
        db.close()


if __name__ == "__main__":
    main()