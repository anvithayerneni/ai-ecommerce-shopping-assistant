from __future__ import annotations

import math
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.embedding_service import embedding_service


# ============================================================
# CATEGORY DESCRIPTIONS
# ============================================================

CATEGORY_DESCRIPTIONS = {
    "Laptops": (
        "laptops, notebook computers, MacBooks, Dell laptops, "
        "Chromebooks, portable computers, business laptops, "
        "gaming laptops and personal computers"
    ),
    "Smartphones": (
        "smartphones, mobile phones, iPhones, Android phones, "
        "cell phones, cellular phones and mobile devices"
    ),
    "Headphones": (
        "headphones, earbuds, earphones, headsets, gaming headsets, "
        "wireless audio devices and noise cancelling headphones"
    ),
    "Running Shoes": (
        "running shoes, athletic footwear, sneakers, trainers, "
        "training shoes, marathon shoes and sports footwear"
    ),
    "Backpacks": (
        "backpacks, school backpacks, laptop backpacks, "
        "travel backpacks and bags worn on the back"
    ),
    "Bags": (
        "bags, handbags, purses, clutch bags, tote bags, "
        "duffel bags, weekender bags, shoulder bags, "
        "crossbody bags, canvas bags, travel bags and luggage"
    ),
    "Jewelry": (
        "jewelry, necklaces, bracelets, rings, earrings, "
        "pendants, crucifixes, charms and other jewelry"
    ),
    "Clothing": (
        "clothing, apparel, shirts, t-shirts, tees, hoodies, "
        "sweatshirts, sweaters, jackets, dresses, pants, "
        "shorts, skirts, tank tops, crop tops, swimsuits, "
        "socks and other garments"
    ),
    "Accessories": (
        "fashion accessories, hats, caps, beanies, belts, "
        "scarves, hair accessories, scrunchies, bonnets "
        "and wearable accessories"
    ),
    "Kitchen": (
        "kitchen products, cookware, cooking utensils, "
        "cutting boards, aprons, kitchen towels, pots, pans "
        "and kitchen equipment"
    ),
    "Drinkware": (
        "drinkware, mugs, coffee mugs, tumblers, cups, "
        "water bottles, thermoses and beverage containers"
    ),
    "Electronics": (
        "consumer electronics, USB devices, speakers, cameras, "
        "LED lights, HDMI devices, chargers, power banks, "
        "cables, adapters and electronic equipment"
    ),
    "Computers & Accessories": (
        "computer accessories, computer hardware, keyboards, "
        "mice, mouse pads, monitors, printers, SATA devices, "
        "hard drives, SSDs, cooling pads, power supplies and "
        "computer peripherals"
    ),
    "Beauty & Personal Care": (
        "beauty products, cosmetics, skincare, makeup, "
        "hair care, deodorant, chapstick, lip balm, "
        "personal care and grooming products"
    ),
    "Health & Wellness": (
        "health and wellness products, oral care, toothpaste, "
        "mouthwash, sinus care, sinus rinse, wellness products, "
        "herbal remedies and personal wellness products"
    ),
    "Food & Beverage": (
        "food and beverage products, tea, tea blends, herbal tea, "
        "honey, snacks, coffee and consumable food products"
    ),
    "Sports & Fitness": (
        "sports equipment, fitness equipment, gym equipment, "
        "exercise equipment, workout gear and athletic accessories"
    ),
    "Cycling": (
        "cycling products, bicycle equipment, bike accessories, "
        "bicycle helmets, cycling helmets, road cycling gear "
        "and mountain biking equipment"
    ),
    "Toys & Games": (
        "toys, children's toys, games, educational toys, "
        "board games, trading cards, Pokemon cards, "
        "collectible cards, booster packs and children's "
        "entertainment products"
    ),
    "Home": (
        "home products, household goods, furniture, decorations, "
        "blankets, rugs, magnets, incense, humidifiers, fans, "
        "alarm clocks, lighting and home decor"
    ),
    "Office": (
        "office supplies, notebooks, journals, planners, "
        "stationery, desk accessories, office equipment "
        "and workplace products"
    ),
    "Pet Supplies": (
        "pet supplies, dog products, cat products, pet accessories "
        "and animal care products"
    ),
    "Outdoor & Camping": (
        "outdoor products, camping equipment, hiking gear, "
        "outdoor recreation equipment, tents and outdoor accessories"
    ),
    "Automotive": (
        "automotive products, car accessories, vehicle equipment, "
        "automotive tools, car seat covers, sun shades, "
        "wheel covers and products for cars and vehicles"
    ),
    "Gift Cards": (
        "gift cards, store gift cards, digital gift cards, "
        "shopping vouchers and gift certificates"
    ),
    "Books": (
        "books, printed books, study books, Bibles, devotional books, "
        "affirmation books, educational books, novels and reading materials"
    ),
    "Music & Media": (
        "music and media, CDs, MP3s, vinyl records, albums, "
        "music recordings, audio media, DVDs and entertainment media"
    ),
    "Religious & Spiritual": (
        "religious and spiritual products, prayer kits, "
        "religious gifts, spiritual items, faith products, "
        "Christian products and religious accessories"
    ),
}


# ============================================================
# PRODUCT-TYPE-FIRST RULES
#
# These rules have higher priority than semantic similarity.
#
# IMPORTANT:
# Words such as "God", "Jesus", "Christian", etc. do NOT
# determine the category by themselves.
#
# The physical/product type wins.
# ============================================================

PRODUCT_TYPE_RULES = {
    "Clothing": [
        "t-shirt",
        "t shirt",
        "tshirt",
        "tee",
        "hoodie",
        "sweatshirt",
        "crewneck",
        "sweater",
        "tank top",
        "tank",
        "muscle tank",
        "racerback",
        "crop top",
        "v-neck",
        "long sleeve",
        "short sleeve",
        "swimsuit",
        "swim suit",
        "one piece swimsuit",
        "one-piece swimsuit",
        "dress",
        "shirt",
        "jacket",
        "pants",
        "trousers",
        "shorts",
        "skirt",
        "socks",
        "sock",
        "leggings",
        "underwear",
        "bra",
        "boxers",
        "briefs",
        "bodysuit",
        "romper",
        "overalls",
        "overol",
        "sudadera",
        "conjunto sudadera",
        "conjunto short",
        "conjunto",
        "ropa",
        "ropa de niña",
        "ropa de niño",
        "ropa bebe",
        "ropa bebé",
        "niña bebé",
        "niño bebé",
        "vestido",
        "womens wear",
        "women's wear",
        "mens wear",
        "men's wear",
        "joggers",
        "turtleneck",
        "top",
        "tops",
        "legging",
        "leggings",
        "biker shorts",
        "biker short",
        "compression leggings",
        "shapewear",
        "pajamas",
        "pajama",
        "dressing robe",
        "dressing gown",
        "robe",
        "thermal clothing",
    ],

    "Accessories": [
        "beanie",
        "cap",
        "hat",
        "baseball cap",
        "dad hat",
        "bucket hat",
        "twill hat",
        "twill cap",
        "snapback",
        "trucker hat",
        "visor",
        "headband",
        "scrunchie",
        "scrunchies",
        "hair tie",
        "hair clip",
        "hair accessory",
        "bonnet",
        "hair bonnet",
        "scarf",
        "belt",
        "sticker",
        "stickers",
        "kiss-cut sticker",
        "kiss-cut stickers",
    ],

    "Bags": [
        "handbag",
        "purse",
        "clutch bag",
        "clutch",
        "tote bag",
        "tote",
        "canvas bag",
        "canvas tote",
        "duffel bag",
        "weekender bag",
        "travel bag",
        "shoulder bag",
        "crossbody bag",
        "luggage",
        "fanny pack",
        "waist bag",
        "belt bag",
    ],

    "Backpacks": [
        "backpack",
        "rucksack",
        "school backpack",
        "laptop backpack",
        "travel backpack",
        "computer backpack",
    ],

    "Laptops": [
        "laptop",
        "macbook",
        "chromebook",
        "notebook computer",
        "gaming laptop",
        "business laptop",
        "portatil",
        "portátil",
        "galaxy book",
        "galaxy book4",
        "galaxy book5",
        "galaxy book pro",
        "galaxy book ultra",
        "dell latitude",
        "dell inspiron",
        "dell xps",
        "thinkpad",
        "lenovo thinkpad",
        "lenovo ideapad",
        "hp pavilion",
        "hp envy",
        "hp elitebook",
        "acer aspire",
        "acer swift",
        "asus vivobook",
        "asus zenbook",
        "chromebook",
        "macbook",
        "macbook air",
        "macbook pro",
        "laptop computer",
        "notebook computer",
        "portable computer",
    ],

    "Smartphones": [
        "smartphone",
        "iphone",
        "android phone",
        "android smartphone",
        "cell phone",
        "mobile phone",
        "galaxy phone",
    ],

    "Headphones": [
        "headphones",
        "headphone",
        "earbuds",
        "earbud",
        "earphones",
        "headset",
        "gaming headset",
        "gaming headphones",
        "diadema",
        "audifonos",
        "audífonos",
        "tws",
    ],

    "Running Shoes": [
        "running shoes",
        "running shoe",
        "marathon shoes",
        "training shoes",
        "athletic footwear",
        "sports footwear",
        "sneakers",
        "trainers",
    ],

    "Jewelry": [
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
    ],

    "Kitchen": [
        "cutting board",
        "apron",
        "kitchen towel",
        "cookware",
        "frying pan",
        "saucepan",
        "kitchen utensil",
        "cooking utensil",
        "cheesecloth",
    ],

    "Drinkware": [
        "mug",
        "coffee mug",
        "tumbler",
        "water bottle",
        "thermos",
        "cup",
        "drinkware",
    ],

    "Electronics": [
        "speaker",
        "parlante",
        "bluetooth speaker",
        "camera",
        "cámara",
        "camara",
        "led strip",
        "led light",
        "hdmi",
        "charger",
        "cargador",
        "power bank",
        "usb device",
        "adapter",
        "cable",
        "laptop charger",
        "laptop chargers",
        "notebook charger",
        "notebook chargers",
        "laptop power adapter",
        "laptop power adapters",
        "laptop adapter",
        "laptop adapters",
        "ac adapter for laptop",
        "ac adapters for laptop",
        "power supply for laptop",
        "power supplies for laptop",
        "charger for laptop",
        "chargers for laptop",
        "cargador para portatil",
        "cargador para portátil",
        "cargador de laptop",
        "cargador de portátil",
    ],

    "Computers & Accessories": [
        "mouse",
        "mouse pad",
        "mousepad",
        "pad mouse",
        "keyboard",
        "teclado",
        "printer",
        "impresora",
        "hard drive",
        "disco duro",
        "ssd",
        "sata",
        "cooling pad",
        "power supply",
        "fuente de poder",
        "computer accessory",
        "computer accessories",
        "computer peripheral",
        "computer peripherals",
    ],

    "Beauty & Personal Care": [
        "skincare",
        "skin care",
        "makeup",
        "cosmetic",
        "shampoo",
        "conditioner",
        "hair care",
        "deodorant",
        "chapstick",
        "lip balm",
        "personal care",
        "grooming",
        "growth oil",
        "hair oil",
        "body oil",
    ],

    "Health & Wellness": [
        "sinus rinse",
        "sinus relief",
        "sinus care",
        "mouthwash",
        "toothpaste",
        "oral care",
        "detox",
        "cleanse",
        "wellness",
        "ayurvedic",
        "propolis",
        "myrrh",
        "herbal remedy",
        "pain relief",
        "posture corrector",
        "back support brace",
        "support brace",
        "orthopedic brace",
        "back brace",
    ],

    "Food & Beverage": [
        "tea blend",
        "herbal tea",
        "tea bags",
        "tea",
        "honey",
        "coffee beans",
        "coffee",
        "snack",
        "food",
        "beverage",
        "sweetener",
        "monkfruit",
        "jam",
        "jams",
        "apple cider",
        "cider",
        "mocha",
        "peppermint mocha",
        "cinnamon toast",
        "hot sauce",
        "sauce",
        "salsa",
        "jam",
        "cider",
        "soda",
        "beer",
        "coffee",
        "tea",
        "tea blend",
        "peppermint mocha",
        "mustard",
        "habanero",
        "jalapeno",
        "jalapeño",
        "pepper sauce",
        ],

    "Sports & Fitness": [
        "fitness equipment",
        "gym equipment",
        "exercise equipment",
        "workout gear",
        "sports equipment",
        "athletic equipment",
    ],

    "Cycling": [
        "cycling helmet",
        "bicycle helmet",
        "bike helmet",
        "cycling",
        "bicycle",
        "bike",
        "casco",
    ],

    "Toys & Games": [
        "toy",
        "board game",
        "trading card",
        "trading cards",
        "pokemon card",
        "pokemon cards",
        "booster pack",
        "booster box",
        "collectible card",
        "collectible cards",
    ],

    "Home": [
        "rug",
        "rugs",
        "carpet",
        "blanket",
        "throw blanket",
        "plush blanket",
        "magnet",
        "magnets",
        "magnet bundle",
        "incense",
        "incense sticks",
        "palo santo",
        "home decor",
        "home decoration",
        "wall art",
        "humidifier",
        "humidificador",
        "fan",
        "ventilator",
        "ventilador",
        "alarm clock",
        "despertador",
        "lamp",
        "lighting",
        "gingerbread house",
        "painting",
        "pintura",
    ],

    "Office": [
        "notebook",
        "spiral notebook",
        "journal",
        "planner",
        "stationery",
        "notepad",
        "office supplies",
        "desk accessory",
    ],

    "Pet Supplies": [
        "pet supplies",
        "pet accessory",
        "dog product",
        "cat product",
        "dog food",
        "cat food",
        "animal care",
    ],

    "Outdoor & Camping": [
        "camping",
        "tent",
        "sleeping bag",
        "hiking gear",
        "hiking",
        "outdoor equipment",
        "insect repellent",
        "mosquito repellent",
        "bug repellent",
        "tick repellent",
    ],

    "Automotive": [
        "car seat cover",
        "car seat covers",
        "auto sun shade",
        "car sun shade",
        "sun shade",
        "wheel cover",
        "steering wheel cover",
        "car floor mat",
        "floor mat",
        "license plate",
        "car accessory",
        "car accessories",
        "vehicle accessory",
        "vehicle accessories",
        "automotive",
    ],

    "Gift Cards": [
        "gift card",
        "gift certificate",
        "shopping voucher",
        "store voucher",
    ],

    "Books": [
        "book",
        "books",
        "bible",
        "bibles",
        "study bible",
        "devotional book",
        "affirmations book",
        "prayer book",
        "novel",
        "reading book",
    ],

    "Music & Media": [
        "mp3",
        "cd",
        "album",
        "álbum",
        "music",
        "song",
        "vinyl",
        "vinil",
        "vinyl record",
        "record",
        "audio recording",
        "music recording",
        "dvd",
        "reissue",
        "reedição",
        "reedicão",
        "re-edition",
        "mp3",
        "cd",
        "album",
        "álbum",
        "vinyl",
        "vinil",
        "record",
        "music",
        "reissue",
        "reedição",
        "album",
        "álbum",
        "vinyl",
        "vinil",
        "cd",
        "mp3",
        "reissue",
        "reissue",
        "reedição",
        "reedicao",
    ],

    "Religious & Spiritual": [
        "prayer kit",
        "prayer set",
        "anointing oil",
        "holy oil",
        "religious gift",
        "religious product",
        "spiritual product",
    ],
}


# ============================================================
# CATEGORY DESCRIPTIONS ARE USED ONLY AFTER EXPLICIT RULES
# ============================================================


def normalize_text(*values: str | None) -> str:
    text = " ".join(
        value.strip()
        for value in values
        if value
    )

    text = text.lower()

    text = (
        text
        .replace("�", "a")
        .replace("–", "-")
        .replace("—", "-")
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


# ============================================================
# WHOLE WORD / PHRASE MATCHING
# ============================================================

def contains_keyword(
    text: str,
    keyword: str,
) -> bool:

    text = normalize_text(text)
    keyword = normalize_text(keyword)

    if not text or not keyword:
        return False

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

    keyword_length = len(keyword_tokens)

    for index in range(
        len(text_tokens) - keyword_length + 1
    ):
        if (
            text_tokens[
                index:index + keyword_length
            ]
            == keyword_tokens
        ):
            return True

    return False


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:

    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        return 0.0

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )

    norm_a = math.sqrt(
        sum(
            value * value
            for value in vector_a
        )
    )

    norm_b = math.sqrt(
        sum(
            value * value
            for value in vector_b
        )
    )

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (
        norm_a * norm_b
    )


# ============================================================
# SEMANTIC CLASSIFIER
# ============================================================

class SemanticCategoryClassifier:

    def __init__(self) -> None:

        self.categories = list(
            CATEGORY_DESCRIPTIONS.keys()
        )

        self.category_embeddings = {}

        for category in self.categories:

            self.category_embeddings[
                category
            ] = embedding_service.embed_text(
                CATEGORY_DESCRIPTIONS[
                    category
                ]
            )

    # --------------------------------------------------------
    # PRODUCT TYPE FIRST
    # --------------------------------------------------------

    def product_type_category(
        self,
        text: str,
    ) -> tuple[str | None, float]:

        normalized = normalize_text(
            text
        )

        matches = []

        for category, keywords in (
            PRODUCT_TYPE_RULES.items()
        ):

            for keyword in keywords:

                if contains_keyword(
                    normalized,
                    keyword,
                ):

                    matches.append(
                        (
                            category,
                            keyword,
                            len(
                                normalize_text(
                                    keyword
                                )
                            ),
                        )
                    )

        if not matches:
            return None, 0.0

        # Prefer the longest / most specific
        # product-type phrase.
        matches.sort(
            key=lambda item: item[2],
            reverse=True,
        )

        best_category = matches[0][0]

        return (
            best_category,
            1.0,
        )

    # --------------------------------------------------------
    # SEMANTIC CLASSIFICATION
    # --------------------------------------------------------

    def semantic_scores(
        self,
        text: str,
    ) -> list[tuple[str, float]]:

        text_embedding = (
            embedding_service.embed_text(
                normalize_text(text)
            )
        )

        scores = []

        for category in self.categories:

            score = cosine_similarity(
                text_embedding,
                self.category_embeddings[
                    category
                ],
            )

            scores.append(
                (
                    category,
                    score,
                )
            )

        scores.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return scores

    # --------------------------------------------------------
    # MAIN CLASSIFICATION
    # --------------------------------------------------------

    def classify(
        self,
        text: str,
    ) -> list[tuple[str, float]]:

        normalized = normalize_text(
            text
        )

        # ====================================================
        # STEP 1: PRODUCT TYPE
        # ====================================================

        product_category, product_score = (
            self.product_type_category(
                normalized
            )
        )

        if product_category is not None:

            semantic = self.semantic_scores(
                normalized
            )

            remaining = [
                item
                for item in semantic
                if item[0] != product_category
            ]

            return [
                (
                    product_category,
                    product_score,
                ),
                *remaining,
            ]

        # ====================================================
        # STEP 2: SEMANTIC
        # ====================================================

        return self.semantic_scores(
            normalized
        )


# ============================================================
# DECISION
# ============================================================

def classify_with_decision(
    classifier: SemanticCategoryClassifier,
    text: str,
    semantic_score_threshold: float = 0.45,
    semantic_margin_threshold: float = 0.10,
) -> dict:

    results = classifier.classify(
        text
    )

    if not results:

        return {
            "category": None,
            "score": 0.0,
            "second_category": None,
            "second_score": 0.0,
            "margin": 0.0,
            "decision": "REVIEW",
        }

    category, score = results[0]

    if len(results) > 1:

        second_category, second_score = (
            results[1]
        )

    else:

        second_category = None
        second_score = 0.0

    margin = (
        score - second_score
    )

    # Product-type matches are deterministic.
    if score >= 1.0:

        decision = "ACCEPT"

    elif (
        score >= semantic_score_threshold
        and margin >= semantic_margin_threshold
    ):

        decision = "ACCEPT"

    else:

        decision = "REVIEW"

    return {
        "category": category,
        "score": score,
        "second_category": second_category,
        "second_score": second_score,
        "margin": margin,
        "decision": decision,
    }


# ============================================================
# TEST CASES
# ============================================================

if __name__ == "__main__":

    classifier = (
        SemanticCategoryClassifier()
    )

    tests = [
        "God is Unlimited 2 Embroidered Beanie",
        "God is Unlimited Embroidered Beanie",
        "Conjunto Capota Fresita Niña Bebe",
        "Cheesecloth",
        "ISHERBAL Growth Oil",
        "Mura & Stereossauro ADAMAS",
        "VINIL In Gods Hands Vol I",
        "Pintura Desassossego",
        "Vintage Cotton Twill Cap",
        "Bucket Hat",
        "Team Jesus Unisex Twill Hat",
        "Then God Made Woman One Piece Swimsuit",
        "Admit It Life Would Be Boring Without Me Tee",
        "Calming Tea Blend",
        "Sinus Rinse",
        "Sublimation Socks",
        "Bible NIV Study Bible",
        "Affirmations book",
        "Real Ones Mp3 By P.U.R.E.",
        "Penta CD",
        "Prayer Kit",
        "Anointing Oil Gift Set",
        "Car Seat Covers",
        "Auto Sun Shade",
        "Wheel Cover",
    ]

    for text in tests:

        result = classify_with_decision(
            classifier,
            text,
        )

        print()
        print(
            f"TEXT: {text}"
        )

        print(
            f"Category: "
            f"{result['category']}"
        )

        print(
            f"Score: "
            f"{result['score']:.4f}"
        )

        print(
            f"Second: "
            f"{result['second_category']} "
            f"{result['second_score']:.4f}"
        )

        print(
            f"Margin: "
            f"{result['margin']:.4f}"
        )

        print(
            f"Decision: "
            f"{result['decision']}"
        )