from __future__ import annotations

from dataclasses import dataclass

import torch

from app.services.recommendation_features import (
    build_recommendation_features,
)
from app.services.recommendation_representation import (
    build_product_representation,
)
from app.services.recommendation_similarity import (
    hybrid_similarity,
)
from app.services.recommendation_model import (
    ProductEncoder,
)


@dataclass(frozen=True)
class ProductRecommendation:
    product_id: int | str
    score: float


def _encode_structured_features(
    product,
    model: ProductEncoder,
    source_embedding=None,
) -> tuple[list[float], list[float] | None]:
    features = build_recommendation_features(
        product,
        source_embedding=source_embedding,
    )

    representation = build_product_representation(
        features,
    )

    tensor = torch.tensor(
        [representation.vector],
        dtype=torch.float32,
    )

    model.eval()

    with torch.no_grad():
        encoded = model(tensor)

    return (
        encoded.squeeze(0).tolist(),
        representation.semantic_embedding,
    )


def score_product_pair(
    product_a,
    product_b,
    model: ProductEncoder,
    *,
    embedding_a=None,
    embedding_b=None,
    semantic_weight: float = 0.7,
    structured_weight: float = 0.3,
) -> float:
    """
    Calculate a hybrid similarity score between two products.
    """

    structured_a, semantic_a = _encode_structured_features(
        product_a,
        model,
        source_embedding=embedding_a,
    )

    structured_b, semantic_b = _encode_structured_features(
        product_b,
        model,
        source_embedding=embedding_b,
    )

    semantic_score = 0.0

    if semantic_a is not None and semantic_b is not None:
        from app.services.recommendation_similarity import (
            semantic_similarity,
        )

        semantic_score = semantic_similarity(
            semantic_a,
            semantic_b,
        )

    from app.services.recommendation_similarity import (
        structured_similarity,
    )

    structured_score = structured_similarity(
        structured_a,
        structured_b,
    )

    return hybrid_similarity(
        semantic_score=semantic_score,
        structured_score=structured_score,
        semantic_weight=semantic_weight,
        structured_weight=structured_weight,
    )


def recommend_similar_products(
    query_product,
    candidate_products,
    model: ProductEncoder,
    *,
    query_embedding=None,
    candidate_embeddings: dict[int | str, list[float]] | None = None,
    top_k: int = 5,
) -> list[ProductRecommendation]:
    """
    Recommend products similar to query_product.

    The query product itself is excluded from the results.
    """

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    candidate_embeddings = candidate_embeddings or {}

    recommendations: list[ProductRecommendation] = []

    for product in candidate_products:
        if product.id == query_product.id:
            continue

        score = score_product_pair(
            query_product,
            product,
            model,
            embedding_a=query_embedding,
            embedding_b=candidate_embeddings.get(
                product.id
            ),
        )

        recommendations.append(
            ProductRecommendation(
                product_id=product.id,
                score=score,
            )
        )

    recommendations.sort(
        key=lambda recommendation: recommendation.score,
        reverse=True,
    )

    return recommendations[:top_k]
