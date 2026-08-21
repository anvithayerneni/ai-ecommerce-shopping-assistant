from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.session import SessionLocal
from app.models.product import Product


# These are the original manually enriched products.
PRESERVE_IDS = set(range(1, 12))


def main() -> None:
    db = SessionLocal()

    try:
        products = (
            db.query(Product)
            .filter(Product.id.notin_(PRESERVE_IDS))
            .filter(Product.category.isnot(None))
            .all()
        )

        print(
            f"Products that would be rolled back: "
            f"{len(products)}"
        )

        for product in products[:20]:
            print(
                f"ROLLBACK | "
                f"id={product.id} | "
                f"name={product.name}"
            )

        if len(products) > 20:
            print(
                f"... and {len(products) - 20} more"
            )

        print()
        confirmation = input(
            "Type ROLLBACK to continue: "
        ).strip()

        if confirmation != "ROLLBACK":
            print("Rollback cancelled.")
            return

        for product in products:
            product.category = None
            product.subcategory = None
            product.use_cases = None
            product.tags = None
            product.features = None
            product.search_text = None

        db.commit()

        print()
        print("Rollback complete.")
        print(
            f"Products cleared: {len(products)}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
