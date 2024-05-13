from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.services.recommendation_features import (
    RecommendationFeatures,
)


@dataclass(frozen=True)
class ProductRepresentation:
    product_id: int | str
    vector: list[float]
    semantic_embedding: list[float] | None


def _encode_text_features(text: str) -> np.ndarray:
    """
    Create a lightweight deterministic text representation.

    This is intentionally not the semantic embedding. The semantic
    embedding is kept separately and will be handled by the PyTorch
    recommendation model.
    """

    if not text:
        return np.zeros(3, dtype=np.float32)

    text_lower = text.lower()

    return np.asarray(
        [
            float(len(text_lower)),
            float(len(text_lower.split())),
            float(len(set(text_lower.split()))),
        ],
        dtype=np.float32,
    )


def build_product_representation(
    features: RecommendationFeatures,
) -> ProductRepresentation:
    """
    Convert recommendation features into a fixed-size structured vector.

    Structured vector:

        [normalized_price,
         normalized_rating,
         text_length,
         word_count,
         unique_word_count]
    """

    text_features = _encode_text_features(features.text)

    vector = np.concatenate(
        [
            np.asarray(
                [
                    features.normalized_price,
                    features.normalized_rating,
                ],
                dtype=np.float32,
            ),
            text_features,
        ]
    )

    return ProductRepresentation(
        product_id=features.product_id,
        vector=vector.tolist(),
        semantic_embedding=features.embedding,
    )
