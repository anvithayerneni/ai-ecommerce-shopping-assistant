from __future__ import annotations

import re

from app.services.recommendation_similarity import (
    semantic_similarity,
)


# ============================================================
# TEXT HELPERS
# ============================================================

def _normalize_text(value: str | None) -> str:
    if not value:
        return ""

    return value.strip().lower()


def _tokenize(value: str | None) -> set[str]:
    if not value:
        return set()

    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if token
    }


# ============================================================
# PRODUCT ROLE
# ============================================================

def _product_role(product) -> str:
    """
    Identify the functional role of a product.

    Product-specific rules are evaluated before broad
    laptop/electronics rules so accessories are not
    incorrectly classified as primary products.
    """

    text = " ".join(
        value
        for value in [
            product.name,
            product.subcategory,
            product.description,
            product.tags,
            product.features,
        ]
        if value
    ).lower()

    subcategory = _normalize_text(
        product.subcategory
    )

    # --------------------------------------------------------
    # Laptop carrying/accessory products
    # --------------------------------------------------------

    laptop_accessory_terms = [
        "sleeve",
        "laptop sleeve",
        "laptop case",
        "computer case",
        "carrying case",
        "carrying bag",
        "laptop bag",
        "laptop cover",
        "notebook cover",
        "funda",
        "funda para portatil",
        "funda para portátil",
        "funda portatil",
        "funda portátil",
    ]

    if any(
        term in text
        for term in laptop_accessory_terms
    ):
        return "laptop_accessory"

    # --------------------------------------------------------
    # Computer accessories
    # --------------------------------------------------------

    computer_accessory_terms = [
        "mouse",
        "mouse pad",
        "mousepad",
        "keyboard",
        "webcam",
        "docking station",
        "dock",
        "computer stand",
        "laptop stand",
        "cooling pad",
        "cooling stand",
        "screen protector",
        "monitor stand",
        "monitor arm",
    ]

    if any(
        term in text
        for term in computer_accessory_terms
    ):
        return "computer_accessory"

    # --------------------------------------------------------
    # Chargers / power adapters
    # --------------------------------------------------------

    charger_terms = [
        "charger",
        "charging cable",
        "charging cord",
        "power adapter",
        "power adaptor",
        "adapter",
        "adaptor",
        "cargador",
        "cable de carga",
    ]

    if any(
        term in text
        for term in charger_terms
    ):
        return "charger"

    # --------------------------------------------------------
    # Power banks
    # --------------------------------------------------------

    power_bank_terms = [
        "power bank",
        "powerbank",
        "portable charger",
        "portable battery",
        "battery pack",
        "external battery",
        "backup battery",
        "power station",
    ]

    if any(
        term in text
        for term in power_bank_terms
    ):
        return "power_bank"

    # --------------------------------------------------------
    # Speakers
    # --------------------------------------------------------

    speaker_terms = [
        "speaker",
        "speakers",
        "bluetooth speaker",
        "portable speaker",
        "wireless speaker",
        "usb speaker",
        "parlante",
        "sound bar",
        "soundbar",
        "2.1 speaker",
        "2.1 speakers",
    ]

    if any(
        term in text
        for term in speaker_terms
    ):
        return "speaker"

    # --------------------------------------------------------
    # Headphones / earbuds
    # --------------------------------------------------------

    headphone_terms = [
        "headphones",
        "headphone",
        "earbuds",
        "earbud",
        "earphones",
        "earphone",
        "headset",
        "noise-canceling headphones",
        "noise cancelling headphones",
    ]

    if any(
        term in text
        for term in headphone_terms
    ):
        return "headphones"

    # --------------------------------------------------------
    # Lighting
    # --------------------------------------------------------

    lighting_terms = [
        "led strip",
        "led light",
        "led lights",
        "light strip",
        "lighting",
        "lamp",
        "light bulb",
        "bulb",
        "night light",
        "led",
    ]

    if any(
        term in text
        for term in lighting_terms
    ):
        return "lighting"

    # --------------------------------------------------------
    # Smartphones
    # --------------------------------------------------------

    smartphone_terms = [
        "iphone",
        "galaxy s",
        "smartphone",
        "smart phone",
        "phone",
        "android phone",
        "mobile phone",
        "cell phone",
    ]

    if any(
        term in text
        for term in smartphone_terms
    ):
        return "smartphone"

    # --------------------------------------------------------
    # Smartphone accessories
    # --------------------------------------------------------

    smartphone_accessory_terms = [
        "phone case",
        "phone cover",
        "iphone case",
        "screen protector",
        "phone holder",
        "phone mount",
    ]

    if any(
        term in text
        for term in smartphone_accessory_terms
    ):
        return "smartphone_accessory"

    # --------------------------------------------------------
    # Running footwear
    # --------------------------------------------------------

    running_terms = [
        "running shoes",
        "running shoe",
        "marathon shoes",
        "training shoes",
        "athletic footwear",
        "sports footwear",
        "sneakers",
        "trainers",
    ]

    if any(
        term in text
        for term in running_terms
    ):
        return "running_footwear"

    # --------------------------------------------------------
    # Clothing
    # --------------------------------------------------------

    clothing_terms = [
        "t-shirt",
        "t shirt",
        "tee",
        "hoodie",
        "sweatshirt",
        "sweater",
        "tank top",
        "dress",
        "shirt",
        "jacket",
        "pants",
        "trousers",
        "shorts",
        "skirt",
        "leggings",
        "swimsuit",
        "one piece swimsuit",
        "bodysuit",
        "romper",
        "robe",
        "pajamas",
        "joggers",
    ]

    if any(
        term in text
        for term in clothing_terms
    ):
        return "clothing"

    # --------------------------------------------------------
    # Jewelry
    # --------------------------------------------------------

    jewelry_terms = [
        "bracelet",
        "necklace",
        "earring",
        "earrings",
        "pendant",
        "crucifix",
        "charm",
        "ring",
        "anklet",
        "brooch",
        "collar",
        "collares",
    ]

    if any(
        term in text
        for term in jewelry_terms
    ):
        return "jewelry"

    # --------------------------------------------------------
    # Bags
    # --------------------------------------------------------

    bag_terms = [
        "backpack",
        "backpacks",
        "bag",
        "bags",
        "handbag",
        "tote",
        "purse",
        "crossbody",
        "shoulder bag",
        "travel bag",
    ]

    if any(
        term in text
        for term in bag_terms
    ):
        return "bags"

    # --------------------------------------------------------
    # Hats / caps
    # --------------------------------------------------------

    hat_terms = [
        "hat",
        "cap",
        "beanie",
        "bucket hat",
        "baseball cap",
        "dad hat",
        "fitted hat",
        "fanny pack",
    ]

    if any(
        term in text
        for term in hat_terms
    ):
        return "headwear"

    # --------------------------------------------------------
    # Books / notebooks
    # --------------------------------------------------------

    book_terms = [
    "bible",
    "novel",
    "journal",
    "notebook",
    "devotional",
    "workbook",
]

    if any(
        term in text
        for term in book_terms
    ):
        return "books"

    # --------------------------------------------------------
    # Food / beverages
    # --------------------------------------------------------

    food_terms = [
        "coffee",
        "tea",
        "cider",
        "jam",
        "snack",
        "chocolate",
        "candy",
        "cookie",
        "drink",
        "beverage",
    ]

    if any(
        term in text
        for term in food_terms
    ):
        return "food_beverage"

    # --------------------------------------------------------
    # Primary laptops
    #
    # IMPORTANT:
    # "notebook" is intentionally NOT included here because
    # notebook can mean a physical paper notebook.
    # --------------------------------------------------------

    laptop_terms = [
        "macbook",
        "laptop",
        "thinkpad",
        "latitude",
        "pavilion",
        "aspire",
        "vivobook",
        "galaxy book",
        "chromebook",
        "surface laptop",
        "ultrabook",
    ]

    if (
        any(
            term in text
            for term in laptop_terms
        )
        or "laptop" in subcategory
        or subcategory in {
            "macbook",
            "ultrabook",
            "business laptop",
            "productivity laptop",
        }
    ):
        return "primary_laptop"

    # --------------------------------------------------------
    # Generic fallback
    # --------------------------------------------------------

    return "generic"
# ============================================================
# CATEGORICAL SIMILARITY
# ============================================================

def categorical_similarity(
    product_a,
    product_b,
) -> float:
    """
    Calculate structured similarity using:

    - category
    - subcategory
    - functional product role
    - brand

    Product role receives strong weight because broad
    categories such as Electronics can contain many unrelated
    product types.
    """

    category_a = _normalize_text(
        product_a.category
    )

    category_b = _normalize_text(
        product_b.category
    )

    subcategory_a = _normalize_text(
        product_a.subcategory
    )

    subcategory_b = _normalize_text(
        product_b.subcategory
    )

    brand_a = _normalize_text(
        product_a.brand
    )

    brand_b = _normalize_text(
        product_b.brand
    )

    role_a = _product_role(
        product_a
    )

    role_b = _product_role(
        product_b
    )

    score = 0.0

    # --------------------------------------------------------
    # Broad category
    # --------------------------------------------------------

    if (
        category_a
        and category_b
        and category_a == category_b
    ):
        score += 0.25

    # --------------------------------------------------------
    # Exact subcategory
    # --------------------------------------------------------

    if (
    subcategory_a
    and subcategory_b
    and subcategory_a == subcategory_b
):
    # Generic subcategories should receive a smaller boost.
        generic_subcategories = {
        "headphones",
        "laptop",
        "accessories",
        "electronics",
        "clothing",
        "bags",
        "backpacks",
        "books",
        "home",
        "jewelry",
    }

        if subcategory_a in generic_subcategories:
            score += 0.08
        else:
            score += 0.20

    # --------------------------------------------------------
    # Functional product role
    # --------------------------------------------------------

    if role_a == role_b:
        score += 0.35

    # Primary product ↔ accessory gets only partial
    # similarity.
    elif {
        role_a,
        role_b,
    } in [
        {
            "primary_laptop",
            "laptop_accessory",
        },
        {
            "primary_laptop",
            "charger",
        },
        {
            "primary_laptop",
            "computer_accessory",
        },
        {
            "smartphone",
            "smartphone_accessory",
        },
    ]:
        score += 0.08

    # Same broad electronics category but different
    # functional products should receive no additional
    # role score.
    else:
        score += 0.0

    # --------------------------------------------------------
    # Brand
    # --------------------------------------------------------

    if (
        brand_a
        and brand_b
        and brand_a == brand_b
    ):
        score += 0.10

    return max(
        0.0,
        min(score, 1.0),
    )


# ============================================================
# USE-CASE SIMILARITY
# ============================================================

def use_case_similarity(
    product_a,
    product_b,
) -> float:
    """
    Calculate Jaccard similarity between product use cases.
    """

    use_cases_a = _tokenize(
        product_a.use_cases
    )

    use_cases_b = _tokenize(
        product_b.use_cases
    )

    if (
        not use_cases_a
        or not use_cases_b
    ):
        return 0.0

    intersection = (
        use_cases_a & use_cases_b
    )

    union = (
        use_cases_a | use_cases_b
    )

    if not union:
        return 0.0

    return len(intersection) / len(union)


# ============================================================
# CONTENT SIMILARITY
# ============================================================

def content_similarity(
    product_a,
    product_b,
    *,
    embedding_a: list[float] | None = None,
    embedding_b: list[float] | None = None,
    categorical_weight: float = 0.40,
    use_case_weight: float = 0.20,
    semantic_weight: float = 0.40,
) -> float:
    """
    Calculate content-based product similarity.

    Combines:

        40% categorical metadata
        20% use-case overlap
        40% semantic embedding similarity
    """

    weights = (
        categorical_weight,
        use_case_weight,
        semantic_weight,
    )

    if any(
        weight < 0
        for weight in weights
    ):
        raise ValueError(
            "Similarity weights must be non-negative."
        )

    total_weight = sum(weights)

    if total_weight == 0:
        raise ValueError(
            "At least one similarity weight must be positive."
        )

    categorical_score = (
        categorical_similarity(
            product_a,
            product_b,
        )
    )

    use_case_score = (
        use_case_similarity(
            product_a,
            product_b,
        )
    )

    semantic_score = 0.0

    if (
        embedding_a is not None
        and embedding_b is not None
    ):
        semantic_score = (
            semantic_similarity(
                embedding_a,
                embedding_b,
            )
        )

    score = (
        categorical_score
        * categorical_weight
        + use_case_score
        * use_case_weight
        + semantic_score
        * semantic_weight
    ) / total_weight

    return max(
        0.0,
        min(1.0, score),
    )