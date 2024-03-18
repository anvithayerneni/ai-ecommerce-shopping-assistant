import re
from dataclasses import dataclass


@dataclass
class QueryIntent:
    query: str
    category: str | None = None
    use_case: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_rating: float | None = None


CATEGORY_KEYWORDS = {
    "Running Shoes": [
        "running shoes",
        "running shoe",
        "jogging shoes",
        "training shoes",
    ],
    "Headphones": [
        "headphones",
        "headphone",
        "noise cancelling headphones",
        "noise cancelling",
        "noise-canceling",
        "earphones",
    ],
    "Laptops": [
        "laptop",
        "laptops",
        "macbook",
        "notebook computer",
    ],
}


USE_CASE_KEYWORDS = {
    "training": [
        "training",
        "workout",
        "workouts",
        "gym",
        "exercise",
        "fitness",
    ],
    "programming": [
        "programming",
        "program",
        "coding",
        "developer",
        "development",
        "software",
    ],
    "travel": [
        "travel",
        "travelling",
        "traveling",
        "trip",
        "commuting",
        "commute",
    ],
    "office work": [
        "office work",
        "office",
        "work",
        "productivity",
    ],
}


def _detect_from_keywords(
    query: str,
    keyword_map: dict[str, list[str]],
) -> str | None:
    normalized_query = query.lower().strip()

    phrases = sorted(
        (
            (keyword, value)
            for value, keywords in keyword_map.items()
            for keyword in keywords
        ),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for keyword, value in phrases:
        if keyword in normalized_query:
            return value

    return None


def detect_category(query: str) -> str | None:
    return _detect_from_keywords(
        query,
        CATEGORY_KEYWORDS,
    )


def detect_use_case(query: str) -> str | None:
    return _detect_from_keywords(
        query,
        USE_CASE_KEYWORDS,
    )


def detect_max_price(query: str) -> float | None:
    normalized_query = query.lower()

    patterns = [
        r"under\s+\$?([\d,]+(?:\.\d+)?)",
        r"below\s+\$?([\d,]+(?:\.\d+)?)",
        r"less than\s+\$?([\d,]+(?:\.\d+)?)",
        r"up to\s+\$?([\d,]+(?:\.\d+)?)",
        r"budget\s+(?:of\s+)?\$?([\d,]+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized_query)

        if match:
            return float(match.group(1).replace(",", ""))

    return None


def detect_price_range(
    query: str,
) -> tuple[float | None, float | None]:
    normalized_query = query.lower()

    range_pattern = (
        r"between\s+\$?([\d,]+(?:\.\d+)?)"
        r"\s+and\s+\$?([\d,]+(?:\.\d+)?)"
    )

    match = re.search(
        range_pattern,
        normalized_query,
    )

    if match:
        min_price = float(
            match.group(1).replace(",", "")
        )
        max_price = float(
            match.group(2).replace(",", "")
        )

        return min_price, max_price

    return None, None


def detect_min_price(query: str) -> float | None:
    normalized_query = query.lower()

    patterns = [
        r"over\s+\$?([\d,]+(?:\.\d+)?)",
        r"above\s+\$?([\d,]+(?:\.\d+)?)",
        r"more than\s+\$?([\d,]+(?:\.\d+)?)",
        r"starting at\s+\$?([\d,]+(?:\.\d+)?)",
        r"at least\s+\$?([\d,]+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized_query)

        if match:
            return float(
                match.group(1).replace(",", "")
            )

    return None


def detect_min_rating(query: str) -> float | None:
    normalized_query = query.lower()

    patterns = [
        r"rating\s+(?:of\s+)?(?:at least|above|over)\s+([0-5](?:\.\d+)?)",
        r"rated\s+(?:at least|above|over)\s+([0-5](?:\.\d+)?)",
        r"([0-5](?:\.\d+)?)\s*\+\s*rating",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized_query)

        if match:
            return float(match.group(1))

    return None

def understand_query(query: str) -> QueryIntent:
    min_price, max_price = detect_price_range(query)

    if min_price is None:
        min_price = detect_min_price(query)

    if max_price is None:
        max_price = detect_max_price(query)

    return QueryIntent(
        query=query,
        category=detect_category(query),
        use_case=detect_use_case(query),
        min_price=min_price,
        max_price=max_price,
        min_rating=detect_min_rating(query),
    )