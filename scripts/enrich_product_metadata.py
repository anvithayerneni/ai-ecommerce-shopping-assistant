from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.session import SessionLocal
from app.models.product import Product
from app.services.product_service import build_search_text

from scripts.semantic_category_classifier import (
    SemanticCategoryClassifier,
    classify_with_decision,
)


DEFAULT_LIMIT = 1000

SEMANTIC_SCORE_THRESHOLD = 0.45
SEMANTIC_MARGIN_THRESHOLD = 0.10


# ============================================================
# SUBCATEGORY RULES
# ============================================================

SUBCATEGORY_RULES = {
    "Clothing": {
        "Bra / Intimates": [
            "bra",
            "bralette",
            "lingerie",
            "underwear",
            "panties",
        ],
        "T-Shirt": [
            "t-shirt",
            "t shirt",
            "tee",
        ],
        "Hoodie": [
            "hoodie",
        ],
        "Sweatshirt": [
            "sweatshirt",
            "crewneck",
            "sudadera",
        ],
        "Tank Top": [
            "tank top",
            "tank",
            "racerback",
            "muscle tank",
        ],
        "Dress": [
            "dress",
            "vestido",
        ],
        "Jacket": [
            "jacket",
            "coat",
        ],
        "Pants": [
            "pants",
            "trousers",
            "leggings",
        ],
        "Shorts": [
            "shorts",
        ],
        "Skirt": [
            "skirt",
        ],
        "Socks": [
            "socks",
            "sock",
        ],
        "Children's Clothing": [
            "kids",
            "children",
            "child",
            "boy",
            "girl",
            "niño",
            "niña",
            "bebe",
            "bebé",
            "niña bebé",
            "niño bebé",
            "ropa de niña",
            "ropa de niño",
            "ropa bebe",
            "ropa bebé",
        ],
    },

    "Accessories": {
        "Cap": [
            "cap",
            "snapback",
            "trucker cap",
        ],
        "Hat": [
            "hat",
            "beanie",
        ],
        "Scarf": [
            "scarf",
        ],
        "Belt": [
            "belt",
        ],
    },

    "Jewelry": {
        "Necklace": [
            "necklace",
            "crucifix",
            "pendant",
        ],
        "Bracelet": [
            "bracelet",
        ],
        "Earrings": [
            "earring",
            "earrings",
        ],
        "Ring": [
            "ring",
        ],
    },

    "Bags": {
        "Tote Bag": [
            "tote bag",
            "tote",
            "canvas tote",
        ],
        "Handbag": [
            "handbag",
            "purse",
        ],
        "Clutch Bag": [
            "clutch",
        ],
        "Travel Bag": [
            "travel bag",
            "weekender",
            "duffel",
        ],
        "Laptop Bag": [
            "laptop bag",
            "computer bag",
            "computer briefcase",
            "briefcase",
        ],
        "Canvas Bag": [
            "canvas bag",
        ],
        "Bag": [
            "bag",
            "bolso",
        ],
    },

    "Backpacks": {
        "Laptop Backpack": [
            "laptop backpack",
            "computer backpack",
        ],
        "Travel Backpack": [
            "travel backpack",
        ],
        "School Backpack": [
            "school backpack",
        ],
        "Backpack": [
            "backpack",
            "rucksack",
        ],
    },

    "Laptops": {
        "MacBook": [
            "macbook",
        ],
        "Gaming Laptop": [
            "gaming laptop",
            "gaming notebook",
        ],
        "Business Laptop": [
            "business laptop",
            "latitude",
            "thinkpad",
            "elitebook",
        ],
        "Ultrabook": [
            "ultrabook",
        ],
        "Laptop": [
            "laptop",
            "notebook computer",
            "portatil",
            "portátil",
        ],
    },

    "Smartphones": {
        "iPhone": [
            "iphone",
        ],
        "Android Smartphone": [
            "android",
            "galaxy",
        ],
        "Smartphone": [
            "smartphone",
            "mobile phone",
            "cell phone",
        ],
    },

    "Headphones": {
        "Gaming Headset": [
            "gaming headset",
            "gaming headphones",
            "gamer headset",
        ],
        "Noise-Canceling Headphones": [
            "noise cancelling",
            "noise-canceling",
            "anc",
        ],
        "Earbuds": [
            "earbuds",
            "earbud",
            "tws",
            "earphones",
            "audifonos",
            "audífonos",
        ],
        "Wireless Headphones": [
            "wireless headphones",
            "bluetooth headphones",
        ],
        "Headphones": [
            "headphones",
            "headset",
            "diadema",
        ],
    },

    "Running Shoes": {
        "Marathon Running Shoes": [
            "marathon",
        ],
        "Training Shoes": [
            "training shoes",
            "trainers",
        ],
        "Running Shoes": [
            "running shoes",
            "running shoe",
        ],
    },

    "Drinkware": {
        "Mug": [
            "mug",
            "coffee mug",
        ],
        "Tumbler": [
            "tumbler",
        ],
        "Water Bottle": [
            "water bottle",
            "bottle",
        ],
        "Thermos": [
            "thermos",
        ],
    },

    "Kitchen": {
        "Cutting Board": [
            "cutting board",
        ],
        "Apron": [
            "apron",
        ],
        "Kitchen Towel": [
            "kitchen towel",
        ],
        "Cookware": [
            "cookware",
            "frying pan",
            "saucepan",
            "pot",
        ],
    },

    "Office": {
        "Notebook": [
            "notebook",
            "spiral notebook",
        ],
        "Journal": [
            "journal",
        ],
        "Planner": [
            "planner",
        ],
        "Book / Guide": [
            "book",
            "guide",
            "blueprint",
            "manual",
        ],
        "Stationery": [
            "stationery",
            "notepad",
        ],
    },

    "Home": {
        "Rug": [
            "rug",
            "rugs",
            "carpet",
        ],
        "Blanket": [
            "blanket",
            "throw blanket",
            "plush blanket",
        ],
        "Magnet": [
            "magnet",
            "magnets",
            "magnet bundle",
        ],
        "Incense": [
            "incense",
            "incense sticks",
            "palo santo",
        ],
        "Home Decor": [
            "home decor",
            "decoration",
            "wall art",
        ],
        "Lighting": [
            "lamp",
            "lighting",
        ],
        "Humidifier": [
            "humidifier",
            "humidificador",
        ],
        "Fan": [
            "fan",
            "ventilator",
            "ventilador",
        ],
        "Alarm Clock": [
            "alarm clock",
            "despertador",
        ],
    },

    "Electronics": {
        "Camera": [
            "camera",
            "cámara",
            "camara",
        ],
        "Speaker": [
            "speaker",
            "parlante",
        ],
        "LED Lighting": [
            "led strip",
            "led light",
        ],
        "Charger": [
            "charger",
            "cargador",
        ],
        "HDMI Device": [
            "hdmi",
        ],
        "Digital Product": [
            "wallpaper",
            "digital download",
            "digital product",
            "preset",
        ],
    },

    "Computers & Accessories": {
        "Mouse": [
            "mouse",
            "mice",
            "mouse pad",
            "pad mouse",
            "mousepad",
        ],
        "Keyboard": [
            "keyboard",
            "teclado",
        ],
        "Storage": [
            "hard drive",
            "disco duro",
            "ssd",
            "sata",
        ],
        "Printer": [
            "printer",
            "impresora",
        ],
        "Power Supply": [
            "power supply",
            "fuente de poder",
        ],
        "Cooling Pad": [
            "cooling pad",
            "soporte refrigerante",
        ],
        "Computer Accessory": [
            "computer accessory",
            "computer accessories",
            "computer peripheral",
            "computer peripherals",
        ],
    },

    "Cycling": {
        "Cycling Helmet": [
            "cycling helmet",
            "bike helmet",
            "bicycle helmet",
            "casco",
        ],
        "Cycling Accessories": [
            "cycling accessory",
            "bike accessory",
            "bicycle accessory",
        ],
    },

    "Toys & Games": {
        "Trading Cards": [
            "trading card",
            "trading cards",
            "collectible card",
            "collectible cards",
            "pokemon card",
            "pokemon cards",
        ],
        "Booster Pack": [
            "booster pack",
        ],
        "Booster Box": [
            "booster box",
        ],
        "Board Game": [
            "board game",
        ],
    },

    "Automotive": {
        "Car Seat Cover": [
            "car seat cover",
            "car seat covers",
        ],
        "Floor Mat": [
            "floor mat",
            "car floor mat",
        ],
        "License Plate": [
            "license plate",
        ],
        "Vehicle Accessory": [
            "car accessory",
            "car accessories",
            "vehicle accessory",
            "vehicle accessories",
            "auto accessory",
        ],
        "Sun Shade": [
            "sun shade",
            "auto sun shade",
        ],
    },

    "Sports & Fitness": {
        "Fitness Equipment": [
            "fitness equipment",
            "gym equipment",
            "exercise equipment",
        ],
        "Sports Equipment": [
            "sports equipment",
            "athletic equipment",
        ],
    },

    "Outdoor & Camping": {
        "Camping Equipment": [
            "camping",
            "tent",
            "sleeping bag",
        ],
        "Hiking Gear": [
            "hiking",
            "hiking gear",
        ],
    },

    "Beauty & Personal Care": {
        "Skincare": [
            "skincare",
            "skin care",
        ],
        "Hair Care": [
            "hair care",
            "shampoo",
            "conditioner",
        ],
        "Cosmetics": [
            "makeup",
            "cosmetic",
        ],
        "Personal Care": [
            "deodorant",
            "chapstick",
            "lip balm",
        ],
    },

    "Health & Wellness": {
        "Oral Care": [
            "toothpaste",
            "mouthwash",
            "oral care",
        ],
        "Sinus Care": [
            "sinus rinse",
            "sinus relief",
        ],
        "Wellness": [
            "detox",
            "cleanse",
            "wellness",
            "ayurvedic",
        ],
    },

    "Food & Beverage": {
        "Tea": [
            "tea",
            "tea blend",
            "herbal tea",
            "tea bags",
        ],
        "Honey": [
            "honey",
        ],
        "Coffee": [
            "coffee beans",
            "coffee",
        ],
    },

    "Gift Cards": {
        "Gift Card": [
            "gift card",
            "gift certificate",
            "shopping voucher",
        ],
    },
}


# ============================================================
# USE CASES
# ============================================================

USE_CASE_RULES = {
    "Clothing": (
        "casual wear, everyday wear, fashion"
    ),
    "Accessories": (
        "fashion, everyday wear, personal accessories"
    ),
    "Jewelry": (
        "fashion, gifting, personal accessories"
    ),
    "Bags": (
        "travel, commuting, carrying belongings"
    ),
    "Backpacks": (
        "school, commuting, travel, carrying belongings"
    ),
    "Laptops": (
        "programming, studying, office work, productivity"
    ),
    "Smartphones": (
        "communication, photography, entertainment, mobile work"
    ),
    "Headphones": (
        "music, travel, commuting, entertainment"
    ),
    "Running Shoes": (
        "running, training, fitness"
    ),
    "Drinkware": (
        "drinking beverages, home use, office use"
    ),
    "Kitchen": (
        "cooking, food preparation, home use"
    ),
    "Office": (
        "office work, studying, organization"
    ),
    "Home": (
        "home use, household use, decoration"
    ),
    "Electronics": (
        "technology, entertainment, productivity"
    ),
    "Computers & Accessories": (
        "computing, office work, productivity"
    ),
    "Cycling": (
        "cycling, exercise, outdoor recreation"
    ),
    "Toys & Games": (
        "gaming, collecting, entertainment"
    ),
    "Automotive": (
        "driving, vehicle use, automotive maintenance"
    ),
    "Sports & Fitness": (
        "exercise, training, fitness"
    ),
    "Outdoor & Camping": (
        "camping, hiking, outdoor recreation"
    ),
    "Beauty & Personal Care": (
        "personal care, grooming, beauty"
    ),
    "Health & Wellness": (
        "personal wellness, health care, daily care"
    ),
    "Food & Beverage": (
        "food, beverages, home use"
    ),
    "Gift Cards": (
        "gifting, shopping"
    ),
}


# ============================================================
# FEATURE RULES
# ============================================================

FEATURE_RULES = {
    "wireless": "wireless connectivity",
    "bluetooth": "Bluetooth connectivity",
    "usb": "USB connectivity",
    "portable": "portable design",
    "lightweight": "lightweight design",
    "waterproof": "waterproof construction",
    "water resistant": "water-resistant construction",
    "noise cancelling": "noise cancellation",
    "noise-canceling": "noise cancellation",
    "rechargeable": "rechargeable battery",
    "led": "LED lighting",
    "stainless steel": "stainless steel construction",
    "insulated": "insulated construction",
}


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(
    *values: str | None,
) -> str:

    text = " ".join(
        value.strip()
        for value in values
        if value
    )

    text = text.lower()

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def contains_keyword(
    text: str,
    keyword: str,
) -> bool:

    text = normalize_text(text)
    keyword = normalize_text(keyword)

    if not text or not keyword:
        return False

    if keyword in text:
        return True

    text_tokens = re.findall(
        r"[a-z0-9]+",
        text,
    )

    keyword_tokens = re.findall(
        r"[a-z0-9]+",
        keyword,
    )

    if not keyword_tokens:
        return False

    if len(keyword_tokens) == 1:
        return keyword_tokens[0] in text_tokens

    length = len(keyword_tokens)

    for index in range(
        len(text_tokens) - length + 1
    ):
        if (
            text_tokens[
                index:index + length
            ]
            == keyword_tokens
        ):
            return True

    return False


# ============================================================
# SUBCATEGORY
# ============================================================

def derive_subcategory(
    category: str,
    text: str,
) -> str | None:

    rules = SUBCATEGORY_RULES.get(
        category
    )

    if not rules:
        return None

    matches = []

    for subcategory, keywords in rules.items():

        for keyword in keywords:

            if contains_keyword(
                text,
                keyword,
            ):
                matches.append(
                    (
                        subcategory,
                        keyword,
                        len(
                            normalize_text(
                                keyword
                            )
                        ),
                    )
                )

    if not matches:
        return None

    matches.sort(
        key=lambda item: item[2],
        reverse=True,
    )

    return matches[0][0]


# ============================================================
# VALIDATION
# ============================================================

def validate_subcategory(
    category: str,
    subcategory: str | None,
    text: str,
) -> bool:

    if subcategory is None:
        return True

    rules = SUBCATEGORY_RULES.get(
        category
    )

    if not rules:
        return False

    keywords = rules.get(
        subcategory,
        [],
    )

    return any(
        contains_keyword(
            text,
            keyword,
        )
        for keyword in keywords
    )


# ============================================================
# TAGS
# ============================================================

def derive_tags(
    category: str,
    subcategory: str | None,
    text: str,
) -> str | None:

    tags = []

    if category:
        tags.append(
            category.lower()
        )

    if subcategory:
        tags.append(
            subcategory.lower()
        )

    candidates = [
        "wireless",
        "bluetooth",
        "portable",
        "lightweight",
        "gaming",
        "travel",
        "office",
        "school",
        "fitness",
        "outdoor",
        "waterproof",
        "rechargeable",
        "pokemon",
        "collectible",
        "tea",
        "honey",
        "wellness",
        "oral care",
        "sinus",
        "incense",
        "magnet",
        "socks",
    ]

    for candidate in candidates:

        if contains_keyword(
            text,
            candidate,
        ):
            tags.append(candidate)

    if not tags:
        return None

    return ", ".join(
        dict.fromkeys(tags)
    )


# ============================================================
# FEATURES
# ============================================================

def derive_features(
    text: str,
) -> str | None:

    features = []

    for keyword, feature in (
        FEATURE_RULES.items()
    ):

        if contains_keyword(
            text,
            keyword,
        ):
            features.append(feature)

    if not features:
        return None

    return ", ".join(
        dict.fromkeys(features)
    )


# ============================================================
# PRODUCT TEXT
# ============================================================

def product_text(
    product: Product,
) -> str:

    return normalize_text(
        product.name,
        product.brand,
        product.description,
        product.tags,
        product.features,
        product.target_audience,
        product.use_cases,
    )


# ============================================================
# ENRICH PRODUCT
# ============================================================

def enrich_product(
    product: Product,
    classifier: SemanticCategoryClassifier,
) -> dict:

    text = product_text(product)

    result = classify_with_decision(
        classifier,
        text,
        semantic_score_threshold=(
            SEMANTIC_SCORE_THRESHOLD
        ),
        semantic_margin_threshold=(
            SEMANTIC_MARGIN_THRESHOLD
        ),
    )

    category = result["category"]

    if (
        result["decision"] != "ACCEPT"
        or category is None
    ):
        return {
            "decision": "REVIEW",
            "category": category,
            "subcategory": None,
            "use_cases": None,
            "tags": None,
            "features": None,
            "score": result["score"],
            "margin": result["margin"],
        }

    subcategory = derive_subcategory(
        category,
        text,
    )

    if subcategory is not None:

        if not validate_subcategory(
            category,
            subcategory,
            text,
        ):
            return {
                "decision": "REVIEW",
                "category": category,
                "subcategory": None,
                "use_cases": None,
                "tags": None,
                "features": None,
                "score": result["score"],
                "margin": result["margin"],
            }

    use_cases = USE_CASE_RULES.get(
        category
    )

    tags = derive_tags(
        category,
        subcategory,
        text,
    )

    features = derive_features(
        text
    )

    return {
        "decision": "ACCEPT",
        "category": category,
        "subcategory": subcategory,
        "use_cases": use_cases,
        "tags": tags,
        "features": features,
        "score": result["score"],
        "margin": result["margin"],
    }


# ============================================================
# DATABASE QUERY
# ============================================================

def get_products(
    db: Session,
    limit: int,
) -> list[Product]:

    return (
        db.query(Product)
        .order_by(Product.id)
        .limit(limit)
        .all()
    )


# ============================================================
# DRY RUN
# ============================================================

def run_dry_run(
    db: Session,
    limit: int,
) -> None:

    products = get_products(
        db,
        limit,
    )

    print()
    print(
        "Product Metadata Enrichment"
    )
    print(
        "---------------------------"
    )
    print("Mode: DRY RUN")
    print(
        f"Products evaluated: {len(products)}"
    )
    print()

    classifier = (
        SemanticCategoryClassifier()
    )

    accepted = 0
    review = 0

    for product in products:

        result = enrich_product(
            product,
            classifier,
        )

        if result["decision"] == "ACCEPT":

            accepted += 1

            print(
                f"ACCEPT | "
                f"id={product.id} | "
                f"name={product.name[:70]} | "
                f"category={result['category']} | "
                f"subcategory={result['subcategory']} | "
                f"use_cases={result['use_cases']}"
            )

        else:

            review += 1

            print(
                f"REVIEW | "
                f"id={product.id} | "
                f"name={product.name[:70]} | "
                f"category={result['category']} | "
                f"score={result['score']:.4f} | "
                f"margin={result['margin']:.4f}"
            )

    print()
    print(
        "Enrichment Summary"
    )
    print(
        "------------------"
    )
    print(
        f"Accepted: {accepted}"
    )
    print(
        f"Review:   {review}"
    )

    if products:
        print(
            f"Acceptance rate: "
            f"{accepted / len(products) * 100:.1f}%"
        )

    print()
    print(
        "DRY RUN COMPLETE"
    )
    print(
        "No database changes were made."
    )


# ============================================================
# APPLY
# ============================================================

# ============================================================
# APPLY
# ============================================================

def apply_enrichment(
    db: Session,
    limit: int,
) -> None:

    products = get_products(
        db,
        limit,
    )

    print()
    print(
        "Product Metadata Enrichment"
    )
    print(
        "---------------------------"
    )
    print("Mode: APPLY")
    print(
        f"Products evaluated: {len(products)}"
    )
    print()

    classifier = (
        SemanticCategoryClassifier()
    )

    accepted = 0
    review = 0

    try:

        for product in products:

            # Reprocess every product so improved
            # classification rules can correct
            # previously assigned metadata.
            print(
                f"REPROCESS | "
                f"id={product.id} | "
                f"name={product.name[:70]}"
            )

            result = enrich_product(
                product,
                classifier,
            )

            # If the classifier is not confident,
            # preserve the existing database metadata.
            if result["decision"] != "ACCEPT":

                review += 1

                print(
                    f"REVIEW | "
                    f"id={product.id} | "
                    f"name={product.name[:70]} | "
                    f"category={result['category']} | "
                    f"score={result['score']:.4f} | "
                    f"margin={result['margin']:.4f}"
                )

                continue

            # ACCEPT:
            # overwrite existing metadata with the
            # newly calculated values.
            product.category = (
                result["category"]
            )

            product.subcategory = (
                result["subcategory"]
            )

            product.use_cases = (
                result["use_cases"]
            )

            product.tags = (
                result["tags"]
            )

            product.features = (
                result["features"]
            )

            product.search_text = (
                build_search_text(product)
            )

            accepted += 1

            print(
                f"UPDATED | "
                f"id={product.id} | "
                f"name={product.name[:70]} | "
                f"category={product.category} | "
                f"subcategory={product.subcategory}"
            )

        db.commit()

    except Exception:

        db.rollback()

        print()
        print(
            "ERROR: Enrichment failed."
        )
        print(
            "Database changes were rolled back."
        )

        raise

    print()
    print(
        "Enrichment Applied"
    )
    print(
        "------------------"
    )
    print(
        f"Updated: {accepted}"
    )
    print(
        f"Review:  {review}"
    )
    print()
    print(
        "Database changes committed."
    )
# ============================================================
# MAIN
# ============================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Enrich products with "
            "validated category metadata."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Write accepted metadata "
            "to PostgreSQL."
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=(
            "Maximum number of products "
            "to process."
        ),
    )

    args = parser.parse_args()

    if args.limit <= 0:
        raise ValueError(
            "--limit must be greater than zero."
        )

    db = SessionLocal()

    try:

        if args.apply:

            apply_enrichment(
                db,
                args.limit,
            )

        else:

            run_dry_run(
                db,
                args.limit,
            )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()