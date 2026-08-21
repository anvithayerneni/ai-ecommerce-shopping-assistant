
from __future__ import annotations

import re
import sys
from pathlib import Path
from sqlalchemy.orm import Session


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from app.db.session import SessionLocal
from app.models.product import Product


ENRICHMENTS = {
    "Air Max Running Shoes": {
        "subcategory": "Road Running",
        "tags": "running, fitness, lightweight, training",
        "features": "cushioned sole, breathable mesh, lightweight design",
        "target_audience": "runners, fitness enthusiasts",
        "use_cases": "daily running, long-distance training, gym",
        "color": "Black",
        "material": "Mesh",
    },
    "Ultraboost Performance Shoes": {
        "subcategory": "Performance Running",
        "tags": "running, performance, cushioning, training",
        "features": "responsive cushioning, supportive upper, energy return",
        "target_audience": "runners, athletes, fitness enthusiasts",
        "use_cases": "daily running, marathon training, road running",
        "color": "White",
        "material": "Primeknit",
    },
    "MacBook Air M3": {
        "subcategory": "Ultrabook",
        "tags": "laptop, productivity, portable, programming",
        "features": "Apple silicon, long battery life, lightweight design",
        "target_audience": "students, developers, professionals",
        "use_cases": "programming, studying, office work, travel",
        "color": "Silver",
        "material": "Aluminum",
    },
    "Galaxy Book4": {
        "subcategory": "Productivity Laptop",
        "tags": "laptop, windows, productivity, portable",
        "features": "portable design, high-resolution display, multitasking",
        "target_audience": "students, professionals, business users",
        "use_cases": "office work, studying, browsing, productivity",
        "color": "Graphite",
        "material": "Aluminum",
    },
    "WH-1000XM5": {
        "subcategory": "Noise-Canceling Headphones",
        "tags": "headphones, wireless, noise cancellation, travel",
        "features": "active noise cancellation, wireless connectivity, long battery life",
        "target_audience": "travelers, professionals, music listeners",
        "use_cases": "travel, commuting, office work, music",
        "color": "Black",
        "material": "Synthetic leather",
    },
    "QuietComfort Headphones": {
        "subcategory": "Noise-Canceling Headphones",
        "tags": "headphones, wireless, comfort, noise cancellation",
        "features": "active noise cancellation, comfortable ear cushions, wireless audio",
        "target_audience": "travelers, commuters, music listeners",
        "use_cases": "travel, commuting, office work, music",
        "color": "Black",
        "material": "Synthetic leather",
    },
    "iPhone 16": {
        "subcategory": "Flagship Smartphone",
        "tags": "smartphone, apple, camera, mobile",
        "features": "advanced camera system, powerful processor, all-day battery",
        "target_audience": "professionals, students, mobile users",
        "use_cases": "photography, communication, entertainment, mobile work",
        "color": "Blue",
        "material": "Aluminum and glass",
    },
    "Galaxy S25": {
        "subcategory": "Flagship Smartphone",
        "tags": "smartphone, android, camera, performance",
        "features": "high-resolution display, advanced cameras, flagship processor",
        "target_audience": "professionals, students, mobile users",
        "use_cases": "photography, gaming, communication, entertainment",
        "color": "Navy",
        "material": "Aluminum and glass",
    },
    "Everyday Travel Backpack": {
        "subcategory": "Laptop Backpack",
        "tags": "backpack, travel, laptop, commuting",
        "features": "padded laptop compartment, multiple pockets, durable construction",
        "target_audience": "students, commuters, travelers",
        "use_cases": "commuting, travel, school, office",
        "color": "Black",
        "material": "Polyester",
    },
    "Premium Coffee Maker": {
        "subcategory": "Drip Coffee Maker",
        "tags": "coffee, kitchen, brewing, home",
        "features": "programmable brewing, consistent temperature, easy controls",
        "target_audience": "coffee enthusiasts, home users, professionals",
        "use_cases": "home brewing, office coffee, morning routine",
        "color": "Stainless Steel",
        "material": "Stainless Steel",
    },
}


def build_search_text(product: Product) -> str:
    return " | ".join(
        value
        for value in [
            product.name,
            product.brand,
            product.category,
            product.subcategory,
            product.description,
            product.tags,
            product.features,
            product.target_audience,
            product.use_cases,
            product.color,
            product.material,
        ]
        if value
    )


def enrich_products() -> None:
    db: Session = SessionLocal()

    try:
        products = db.query(Product).all()

        updated_count = 0

        for product in products:
            enrichment = ENRICHMENTS.get(product.name)

            if not enrichment:
                continue

            for field, value in enrichment.items():
                setattr(product, field, value)

            product.search_text = build_search_text(product)
            updated_count += 1

        db.commit()

        print(f"Enriched {updated_count} products.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    enrich_products()