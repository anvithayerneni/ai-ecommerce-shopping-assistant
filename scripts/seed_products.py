from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.product import Product


PRODUCTS = [
    {
        "name": "Air Max Running Shoes",
        "description": "Lightweight running shoes designed for everyday training and comfortable long-distance runs.",
        "brand": "Nike",
        "category": "Running Shoes",
        "price": 89.99,
        "rating": 4.5,
        "stock": 25,
    },
    {
        "name": "Ultraboost Performance Shoes",
        "description": "Cushioned performance running shoes designed for runners who want comfort and responsive support.",
        "brand": "Adidas",
        "category": "Running Shoes",
        "price": 129.99,
        "rating": 4.7,
        "stock": 18,
    },
    {
        "name": "MacBook Air M3",
        "description": "Thin and lightweight laptop with Apple silicon, long battery life, and a high-resolution display.",
        "brand": "Apple",
        "category": "Laptops",
        "price": 999.99,
        "rating": 4.8,
        "stock": 12,
    },
    {
        "name": "Galaxy Book4",
        "description": "Portable Windows laptop designed for productivity, multitasking, and everyday computing.",
        "brand": "Samsung",
        "category": "Laptops",
        "price": 849.99,
        "rating": 4.4,
        "stock": 15,
    },
    {
        "name": "WH-1000XM5",
        "description": "Wireless over-ear headphones with active noise cancellation and long battery life.",
        "brand": "Sony",
        "category": "Headphones",
        "price": 349.99,
        "rating": 4.8,
        "stock": 10,
    },
    {
        "name": "QuietComfort Headphones",
        "description": "Comfortable wireless headphones with strong noise cancellation for travel and work.",
        "brand": "Bose",
        "category": "Headphones",
        "price": 299.99,
        "rating": 4.6,
        "stock": 14,
    },
    {
        "name": "iPhone 16",
        "description": "Premium smartphone with advanced camera features, powerful performance, and all-day battery life.",
        "brand": "Apple",
        "category": "Smartphones",
        "price": 799.99,
        "rating": 4.7,
        "stock": 20,
    },
    {
        "name": "Galaxy S25",
        "description": "Android smartphone with a high-quality display, advanced cameras, and flagship performance.",
        "brand": "Samsung",
        "category": "Smartphones",
        "price": 799.99,
        "rating": 4.6,
        "stock": 16,
    },
    {
        "name": "Everyday Travel Backpack",
        "description": "Durable backpack with padded laptop storage and multiple compartments for commuting and travel.",
        "brand": "North Face",
        "category": "Backpacks",
        "price": 79.99,
        "rating": 4.5,
        "stock": 30,
    },
    {
        "name": "Premium Coffee Maker",
        "description": "Programmable coffee maker designed for convenient brewing and consistent flavor at home.",
        "brand": "Breville",
        "category": "Coffee Makers",
        "price": 149.99,
        "rating": 4.6,
        "stock": 11,
    },
]


def seed_products() -> None:
    db: Session = SessionLocal()

    try:
        existing_names = {
            product.name for product in db.query(Product).all()
        }

        products_to_add = [
            Product(**product)
            for product in PRODUCTS
            if product["name"] not in existing_names
        ]

        if not products_to_add:
            print("No new products to add.")
            return

        db.add_all(products_to_add)
        db.commit()

        print(f"Added {len(products_to_add)} products.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_products()