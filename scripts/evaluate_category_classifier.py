from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.session import SessionLocal
from app.models.product import Product
from scripts.semantic_category_classifier import (
    SemanticCategoryClassifier,
)


SAMPLE_SIZE = 100


def product_text(product: Product) -> str:
    return " ".join(
        value.strip()
        for value in [
            product.name,
            product.brand,
            product.description,
        ]
        if value
    )


def evaluate(
    db: Session,
    sample_size: int = SAMPLE_SIZE,
) -> None:
    products = (
        db.query(Product)
        .filter(Product.category.is_(None))
        .order_by(Product.id)
        .limit(sample_size)
        .all()
    )

    classifier = SemanticCategoryClassifier()

    accepted = 0
    review = 0

    print()
    print("Semantic Category Classifier Evaluation")
    print("---------------------------------------")
    print(f"Products evaluated: {len(products)}")
    print()

    for product in products:
        text = product_text(product)

        category, score, scores = classifier.classify(
            text
        )

        second_score = (
            scores[1][1]
            if len(scores) > 1
            else 0.0
        )

        margin = score - second_score

        # Conservative initial review policy.
        #
        # These are NOT probabilities. They are semantic
        # similarity signals used to decide which records
        # deserve manual review.
        is_accepted = (
            score >= 0.45
            and margin >= 0.10
        )

        if is_accepted:
            accepted += 1
            status = "ACCEPT"
        else:
            review += 1
            status = "REVIEW"

        second_category = (
            scores[1][0]
            if len(scores) > 1
            else None
        )

        print(
            f"{status} | "
            f"id={product.id} | "
            f"name={product.name[:70]} | "
            f"category={category} | "
            f"score={score:.4f} | "
            f"second={second_category} "
            f"{second_score:.4f} | "
            f"margin={margin:.4f}"
        )

    print()
    print("Evaluation Summary")
    print("------------------")
    print(f"Accepted: {accepted}")
    print(f"Review:   {review}")

    if products:
        acceptance_rate = (
            accepted / len(products) * 100
        )

        print(
            f"Acceptance rate: "
            f"{acceptance_rate:.1f}%"
        )


def main() -> None:
    db = SessionLocal()

    try:
        evaluate(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
