from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RecommendationFeatures:
    """
    Feature representation used by the recommendation engine.

    Structured features are kept separate from the semantic embedding
    so that the recommendation pipeline can combine both signals later.
    """

    product_id: int | str
    normalized_price: float
    normalized_rating: float
    text: str
    embedding: list[float] | None


def _safe_float(value: object) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_price(
    price: object,
    *,
    max_price: float = 1000.0,
) -> float:
    """
    Convert a product price into a robust 0-1 feature.

    Prices above max_price are clipped rather than allowed to dominate
    the recommendation model.
    """

    value = _safe_float(price)

    if value is None or value <= 0:
        return 0.0

    value = min(value, max_price)

    return value / max_price


def normalize_rating(
    rating: object,
) -> float:
    """
    Normalize a 0-5 product rating into a 0-1 feature.
    """

    value = _safe_float(rating)

    if value is None:
        return 0.0

    value = max(0.0, min(value, 5.0))

    return value / 5.0


def build_recommendation_text(product: object) -> str:
    """
    Build a recommendation-oriented text representation.

    Uses only fields that are actually available on the product.
    """

    fields = [
        getattr(product, "name", None),
        getattr(product, "brand", None),
        getattr(product, "category", None),
        getattr(product, "subcategory", None),
        getattr(product, "description", None),
        getattr(product, "tags", None),
        getattr(product, "features", None),
        getattr(product, "target_audience", None),
        getattr(product, "use_cases", None),
        getattr(product, "color", None),
        getattr(product, "material", None),
    ]

    return " | ".join(
        str(value).strip()
        for value in fields
        if value is not None and str(value).strip()
    )


def normalize_embedding(
    embedding: object,
) -> list[float] | None:
    """
    Normalize an existing product embedding to unit length.

    Returns None when no valid embedding is available.
    """

    if embedding is None:
        return None

    try:
        values = [float(value) for value in embedding]
    except (TypeError, ValueError):
        return None

    if not values:
        return None

    vector = np.asarray(values, dtype=np.float32)

    norm = float(np.linalg.norm(vector))

    if not math.isfinite(norm) or norm == 0.0:
        return None

    normalized = vector / norm

    return normalized.tolist()


def build_recommendation_features(
    product: object,
    *,
    source_embedding: object = None,
) -> RecommendationFeatures:
    """
    Build the complete feature representation for one product.
    """

    product_id = getattr(product, "id", None)

    if product_id is None:
        product_id = getattr(product, "external_id", None)

    return RecommendationFeatures(
        product_id=product_id,
        normalized_price=normalize_price(
            getattr(product, "price", None),
        ),
        normalized_rating=normalize_rating(
            getattr(product, "rating", None),
        ),
        text=build_recommendation_text(product),
        embedding=normalize_embedding(source_embedding),
    )