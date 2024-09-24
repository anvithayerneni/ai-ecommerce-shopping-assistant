import sys
from pathlib import Path
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.product import Product
from app.services.product_service import build_search_text


PRODUCTS = [
    {
        "name": "Air Max Running Shoes",
        "description": "Lightweight running shoes designed for everyday training and comfortable long-distance runs.",
        "brand": "Nike",
        "category": "Running Shoes",
        "subcategory": "Road Running",
        "price": 89.99,
        "rating": 4.5,
        "stock": 25,
        "tags": "running, fitness, lightweight, training",
        "features": "cushioned sole, breathable mesh, lightweight design",
        "target_audience": "runners, fitness enthusiasts",
        "use_cases": "daily running, long-distance training, gym",
        "color": "Black",
        "material": "Mesh",
    },
    {
        "name": "Ultraboost Performance Shoes",
        "description": "Cushioned performance running shoes designed for runners who want comfort and responsive support.",
        "brand": "Adidas",
        "category": "Running Shoes",
        "subcategory": "Performance Running",
        "price": 129.99,
        "rating": 4.7,
        "stock": 18,
        "tags": "running, performance, cushioning, training",
        "features": "responsive cushioning, supportive upper, energy return",
        "target_audience": "runners, athletes, fitness enthusiasts",
        "use_cases": "daily running, marathon training, road running",
        "color": "White",
        "material": "Primeknit",
    },
    {
        "name": "MacBook Air M3",
        "description": "Thin and lightweight laptop with Apple silicon, long battery life, and a high-resolution display.",
        "brand": "Apple",
        "category": "Laptops",
        "subcategory": "Ultrabook",
        "price": 999.99,
        "rating": 4.8,
        "stock": 12,
        "tags": "laptop, productivity, portable, programming",
        "features": "Apple silicon, long battery life, lightweight design",
        "target_audience": "students, developers, professionals",
        "use_cases": "programming, studying, office work, travel",
        "color": "Silver",
        "material": "Aluminum",
    },
    {
        "name": "Galaxy Book4",
        "description": "Portable Windows laptop designed for productivity, multitasking, and everyday computing.",
        "brand": "Samsung",
        "category": "Laptops",
        "subcategory": "Productivity Laptop",
        "price": 849.99,
        "rating": 4.4,
        "stock": 15,
        "tags": "laptop, windows, productivity, portable",
        "features": "portable design, high-resolution display, multitasking",
        "target_audience": "students, professionals, business users",
        "use_cases": "office work, studying, browsing, productivity",
        "color": "Graphite",
        "material": "Aluminum",
    },
    {
        "name": "WH-1000XM5",
        "description": "Wireless over-ear headphones with active noise cancellation and long battery life.",
        "brand": "Sony",
        "category": "Headphones",
        "subcategory": "Noise-Canceling Headphones",
        "price": 349.99,
        "rating": 4.8,
        "stock": 10,
        "tags": "headphones, wireless, noise cancellation, travel",
        "features": "active noise cancellation, wireless connectivity, long battery life",
        "target_audience": "travelers, professionals, music listeners",
        "use_cases": "travel, commuting, office work, music",
        "color": "Black",
        "material": "Synthetic leather",
    },
    {
        "name": "QuietComfort Headphones",
        "description": "Comfortable wireless headphones with strong noise cancellation for travel and work.",
        "brand": "Bose",
        "category": "Headphones",
        "subcategory": "Noise-Canceling Headphones",
        "price": 299.99,
        "rating": 4.6,
        "stock": 14,
        "tags": "headphones, wireless, comfort, noise cancellation",
        "features": "active noise cancellation, comfortable ear cushions, wireless audio",
        "target_audience": "travelers, commuters, music listeners",
        "use_cases": "travel, commuting, office work, music",
        "color": "Black",
        "material": "Synthetic leather",
    },
    {
        "name": "iPhone 16",
        "description": "Premium smartphone with advanced camera features, powerful performance, and all-day battery life.",
        "brand": "Apple",
        "category": "Smartphones",
        "subcategory": "Flagship Smartphone",
        "price": 799.99,
        "rating": 4.7,
        "stock": 20,
        "tags": "smartphone, apple, camera, mobile",
        "features": "advanced camera system, powerful processor, all-day battery",
        "target_audience": "professionals, students, mobile users",
        "use_cases": "photography, communication, entertainment, mobile work",
        "color": "Blue",
        "material": "Aluminum and glass",
    },
    {
        "name": "Galaxy S25",
        "description": "Android smartphone with a high-quality display, advanced cameras, and flagship performance.",
        "brand": "Samsung",
        "category": "Smartphones",
        "subcategory": "Flagship Smartphone",
        "price": 799.99,
        "rating": 4.6,
        "stock": 16,
        "tags": "smartphone, android, camera, performance",
        "features": "high-resolution display, advanced cameras, flagship processor",
        "target_audience": "professionals, students, mobile users",
        "use_cases": "photography, gaming, communication, entertainment",
        "color": "Navy",
        "material": "Aluminum and glass",
    },
    {
        "name": "Everyday Travel Backpack",
        "description": "Durable backpack with padded laptop storage and multiple compartments for commuting and travel.",
        "brand": "North Face",
        "category": "Backpacks",
        "subcategory": "Laptop Backpack",
        "price": 79.99,
        "rating": 4.5,
        "stock": 30,
        "tags": "backpack, travel, laptop, commuting",
        "features": "padded laptop compartment, multiple pockets, durable construction",
        "target_audience": "students, commuters, travelers",
        "use_cases": "commuting, travel, school, office",
        "color": "Black",
        "material": "Polyester",
    },
    {
        "name": "Premium Coffee Maker",
        "description": "Programmable coffee maker designed for convenient brewing and consistent flavor at home.",
        "brand": "Breville",
        "category": "Coffee Makers",
        "subcategory": "Drip Coffee Maker",
        "price": 149.99,
        "rating": 4.6,
        "stock": 11,
        "tags": "coffee, kitchen, brewing, home",
        "features": "programmable brewing, consistent temperature, easy controls",
        "target_audience": "coffee enthusiasts, home users, professionals",
        "use_cases": "home brewing, office coffee, morning routine",
        "color": "Stainless Steel",
        "material": "Stainless Steel",
    },
]


def seed_products() -> None:
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        existing_names = {
            product.name for product in db.query(Product).all()
        }

        products_to_add = []
        for product_data in PRODUCTS:
            if product_data["name"] not in existing_names:
                product = Product(**product_data)
                product.search_text = build_search_text(product)
                products_to_add.append(product)

        if not products_to_add:
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